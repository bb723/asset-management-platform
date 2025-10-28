"""
Asset Management Platform
A Flask application for managing entities, buildings, budgets, and documents
for Standard Management Company.
"""
import os
import sys
import logging
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from decimal import Decimal

from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, send_file, jsonify
from msal import ConfidentialClientApplication
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import foundation package
from foundation.auth import login_required

# Import database queries
from database import queries
from models import Entity, Building, BudgetItem, Document

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Microsoft OAuth configuration
MS_CLIENT_ID = os.getenv('MS_CLIENT_ID')
MS_CLIENT_SECRET = os.getenv('MS_CLIENT_SECRET')
MS_TENANT_ID = os.getenv('MS_TENANT_ID')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/auth/callback')
AUTHORITY = f"https://login.microsoftonline.com/{MS_TENANT_ID}"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================================
# Authentication Routes
# ============================================================================

@app.route('/login')
def login():
    """Initiate OAuth login flow"""
    state = secrets.token_hex(16)
    session['state'] = state
    session.permanent = True

    msal_app = ConfidentialClientApplication(
        MS_CLIENT_ID,
        authority=AUTHORITY,
        client_credential=MS_CLIENT_SECRET
    )

    auth_url = msal_app.get_authorization_request_url(
        scopes=['User.Read'],
        redirect_uri=REDIRECT_URI,
        state=state
    )

    response = make_response(redirect(auth_url))
    response.set_cookie('oauth_state', state, secure=True, httponly=True, samesite='Lax', max_age=600)

    logger.info("Initiating OAuth login")
    return response


@app.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback"""
    # Verify state
    state_from_session = session.get('state')
    state_from_cookie = request.cookies.get('oauth_state')
    state_from_request = request.args.get('state')

    if not state_from_request or (state_from_request != state_from_session and state_from_request != state_from_cookie):
        logger.error("State mismatch in OAuth callback")
        flash('Authentication failed: Invalid state', 'error')
        return redirect(url_for('login'))

    # Check for errors
    if 'error' in request.args:
        error = request.args.get('error')
        error_description = request.args.get('error_description', '')
        logger.error(f"OAuth error: {error} - {error_description}")
        flash(f'Authentication failed: {error_description}', 'error')
        return redirect(url_for('login'))

    # Exchange code for token
    code = request.args.get('code')
    if not code:
        logger.error("No authorization code received")
        flash('Authentication failed: No authorization code', 'error')
        return redirect(url_for('login'))

    try:
        msal_app = ConfidentialClientApplication(
            MS_CLIENT_ID,
            authority=AUTHORITY,
            client_credential=MS_CLIENT_SECRET
        )

        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=['User.Read'],
            redirect_uri=REDIRECT_URI
        )

        if 'access_token' in result:
            # Store user info in session
            session['user'] = {
                'name': result.get('id_token_claims', {}).get('name', 'User'),
                'email': result.get('id_token_claims', {}).get('preferred_username', ''),
                'authenticated': True
            }

            logger.info(f"User authenticated: {session['user']['email']}")
            flash('Successfully logged in', 'success')
            return redirect(url_for('home'))
        else:
            error = result.get('error', 'Unknown error')
            error_description = result.get('error_description', '')
            logger.error(f"Token acquisition failed: {error} - {error_description}")
            flash(f'Authentication failed: {error_description}', 'error')
            return redirect(url_for('login'))

    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Log out user"""
    user_email = session.get('user', {}).get('email', 'Unknown')
    session.clear()
    logger.info(f"User logged out: {user_email}")
    flash('Successfully logged out', 'success')
    return redirect(url_for('login'))


# ============================================================================
# Entity Routes
# ============================================================================

@app.route('/')
@app.route('/entities')
@login_required
def home():
    """Landing page / list all entities"""
    try:
        entities_data = queries.get_all_entities()
        entities = [Entity.from_dict(e) for e in entities_data]
        return render_template('entity/list.html', entities=entities)
    except Exception as e:
        logger.error(f"Failed to load entities: {e}", exc_info=True)
        flash('Failed to load entities', 'error')
        return render_template('entity/list.html', entities=[])


@app.route('/entities/create', methods=['GET', 'POST'])
@login_required
def create_entity():
    """Create a new entity"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'error': 'Entity name is required'
                }), 400
            flash('Entity name is required', 'error')
            return render_template('entity/create.html')

        try:
            entity_id = queries.create_entity(name, description)
            logger.info(f"Entity created: {name} (ID: {entity_id})")

            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'entity': {
                        'entity_id': entity_id,
                        'name': name,
                        'description': description
                    }
                })

            flash(f'Successfully created entity: {name}', 'success')
            return redirect(url_for('view_entity', entity_id=entity_id))
        except Exception as e:
            logger.error(f"Failed to create entity: {e}", exc_info=True)

            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'error': 'Failed to create entity'
                }), 500

            flash('Failed to create entity', 'error')

    return render_template('entity/create.html')


@app.route('/entities/<entity_id>')
@login_required
def view_entity(entity_id):
    """View entity with buildings list"""
    try:
        entity_data = queries.get_entity_by_id(entity_id)
        if not entity_data:
            flash('Entity not found', 'error')
            return redirect(url_for('home'))

        entity = Entity.from_dict(entity_data)
        buildings_data = queries.get_buildings_by_entity(entity_id)
        buildings = [Building.from_dict(b) for b in buildings_data]

        # Get share token if exists
        share_token = queries.get_existing_share_token(entity_id)

        return render_template('entity/view.html', entity=entity, buildings=buildings, share_token=share_token)
    except Exception as e:
        logger.error(f"Failed to load entity: {e}", exc_info=True)
        flash('Failed to load entity', 'error')
        return redirect(url_for('home'))


@app.route('/entities/<entity_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entity(entity_id):
    """Edit an existing entity"""
    try:
        entity_data = queries.get_entity_by_id(entity_id)
        if not entity_data:
            flash('Entity not found', 'error')
            return redirect(url_for('home'))

        entity = Entity.from_dict(entity_data)

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()

            if not name:
                flash('Entity name is required', 'error')
                return render_template('entity/edit.html', entity=entity)

            if queries.update_entity(entity_id, name, description):
                logger.info(f"Entity updated: {entity_id}")
                flash(f'Successfully updated entity: {name}', 'success')
                return redirect(url_for('view_entity', entity_id=entity_id))
            else:
                flash('Failed to update entity', 'error')

        return render_template('entity/edit.html', entity=entity)
    except Exception as e:
        logger.error(f"Failed to edit entity: {e}", exc_info=True)
        flash('Failed to edit entity', 'error')
        return redirect(url_for('home'))


@app.route('/entities/<entity_id>/delete', methods=['POST'])
@login_required
def delete_entity(entity_id):
    """Delete an entity"""
    try:
        entity_data = queries.get_entity_by_id(entity_id)
        if not entity_data:
            flash('Entity not found', 'error')
            return redirect(url_for('home'))

        entity_name = entity_data.get('NAME', 'Unknown')

        if queries.delete_entity(entity_id):
            logger.info(f"Entity deleted: {entity_id}")
            flash(f'Successfully deleted entity: {entity_name}', 'success')
        else:
            flash('Failed to delete entity', 'error')

        return redirect(url_for('home'))
    except Exception as e:
        logger.error(f"Failed to delete entity: {e}", exc_info=True)
        flash('Failed to delete entity', 'error')
        return redirect(url_for('home'))


@app.route('/entities/<entity_id>/share')
@login_required
def generate_share_link(entity_id):
    """Generate shareable link for entity"""
    try:
        entity_data = queries.get_entity_by_id(entity_id)
        if not entity_data:
            flash('Entity not found', 'error')
            return redirect(url_for('home'))

        # Check if token already exists
        existing_token = queries.get_existing_share_token(entity_id)

        if existing_token:
            token = existing_token
            logger.info(f"Using existing share token for entity {entity_id}")
        else:
            token = queries.create_share_token(entity_id)
            logger.info(f"Created new share token for entity {entity_id}")

        share_url = url_for('shared_view', token=token, _external=True)
        flash('Shareable link generated', 'success')

        return redirect(url_for('view_entity', entity_id=entity_id))
    except Exception as e:
        logger.error(f"Failed to generate share link: {e}", exc_info=True)
        flash('Failed to generate share link', 'error')
        return redirect(url_for('view_entity', entity_id=entity_id))


@app.route('/entities/<entity_id>/budget')
@login_required
def entity_budget(entity_id):
    """View aggregate budget for all buildings in entity"""
    try:
        entity_data = queries.get_entity_by_id(entity_id)
        if not entity_data:
            flash('Entity not found', 'error')
            return redirect(url_for('home'))

        entity = Entity.from_dict(entity_data)
        budget_data = queries.get_entity_budget(entity_id)

        # Organize budget data by month and category
        budget_by_month = {}
        categories = set()

        for item in budget_data:
            month = item['MONTH_YEAR']
            category = item['CATEGORY']
            amount = float(item['TOTAL_AMOUNT'])

            if month not in budget_by_month:
                budget_by_month[month] = {}

            budget_by_month[month][category] = amount
            categories.add(category)

        # Sort months and categories
        sorted_months = sorted(budget_by_month.keys())
        sorted_categories = sorted(list(categories))

        return render_template('budget/entity_budget.html',
                             entity=entity,
                             budget_by_month=budget_by_month,
                             months=sorted_months,
                             categories=sorted_categories)
    except Exception as e:
        logger.error(f"Failed to load entity budget: {e}", exc_info=True)
        flash('Failed to load entity budget', 'error')
        return redirect(url_for('view_entity', entity_id=entity_id))


# ============================================================================
# Building Routes
# ============================================================================

@app.route('/entities/<entity_id>/buildings/create', methods=['GET', 'POST'])
@login_required
def create_building(entity_id):
    """Create a new building for an entity"""
    try:
        entity_data = queries.get_entity_by_id(entity_id)
        if not entity_data:
            flash('Entity not found', 'error')
            return redirect(url_for('home'))

        entity = Entity.from_dict(entity_data)

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            address = request.form.get('address', '').strip()

            if not name:
                flash('Building name is required', 'error')
                return render_template('building/create.html', entity=entity)

            building_id = queries.create_building(entity_id, name, address)
            logger.info(f"Building created: {name} (ID: {building_id})")
            flash(f'Successfully created building: {name}', 'success')
            return redirect(url_for('view_entity', entity_id=entity_id))

        return render_template('building/create.html', entity=entity)
    except Exception as e:
        logger.error(f"Failed to create building: {e}", exc_info=True)
        flash('Failed to create building', 'error')
        return redirect(url_for('view_entity', entity_id=entity_id))


@app.route('/buildings/<building_id>')
@login_required
def view_building(building_id):
    """View building with budget and documents tabs"""
    try:
        building_data = queries.get_building_by_id(building_id)
        if not building_data:
            flash('Building not found', 'error')
            return redirect(url_for('home'))

        building = Building.from_dict(building_data)

        # Get entity info
        entity_data = queries.get_entity_by_id(building.entity_id)
        entity = Entity.from_dict(entity_data) if entity_data else None

        # Get active tab from query parameter
        active_tab = request.args.get('tab', 'budget')

        return render_template('building/view.html',
                             building=building,
                             entity=entity,
                             active_tab=active_tab)
    except Exception as e:
        logger.error(f"Failed to load building: {e}", exc_info=True)
        flash('Failed to load building', 'error')
        return redirect(url_for('home'))


@app.route('/buildings/<building_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_building(building_id):
    """Edit an existing building"""
    try:
        building_data = queries.get_building_by_id(building_id)
        if not building_data:
            flash('Building not found', 'error')
            return redirect(url_for('home'))

        building = Building.from_dict(building_data)

        # Get entity info
        entity_data = queries.get_entity_by_id(building.entity_id)
        entity = Entity.from_dict(entity_data) if entity_data else None

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            address = request.form.get('address', '').strip()

            if not name:
                flash('Building name is required', 'error')
                return render_template('building/edit.html', building=building, entity=entity)

            if queries.update_building(building_id, name, address):
                logger.info(f"Building updated: {building_id}")
                flash(f'Successfully updated building: {name}', 'success')
                return redirect(url_for('view_building', building_id=building_id))
            else:
                flash('Failed to update building', 'error')

        return render_template('building/edit.html', building=building, entity=entity)
    except Exception as e:
        logger.error(f"Failed to edit building: {e}", exc_info=True)
        flash('Failed to edit building', 'error')
        return redirect(url_for('home'))


@app.route('/buildings/<building_id>/delete', methods=['POST'])
@login_required
def delete_building(building_id):
    """Delete a building"""
    try:
        building_data = queries.get_building_by_id(building_id)
        if not building_data:
            flash('Building not found', 'error')
            return redirect(url_for('home'))

        entity_id = building_data.get('ENTITY_ID')
        building_name = building_data.get('NAME', 'Unknown')

        if queries.delete_building(building_id):
            logger.info(f"Building deleted: {building_id}")
            flash(f'Successfully deleted building: {building_name}', 'success')
        else:
            flash('Failed to delete building', 'error')

        return redirect(url_for('view_entity', entity_id=entity_id))
    except Exception as e:
        logger.error(f"Failed to delete building: {e}", exc_info=True)
        flash('Failed to delete building', 'error')
        return redirect(url_for('home'))


# ============================================================================
# Budget Routes
# ============================================================================

@app.route('/buildings/<building_id>/budget')
@login_required
def view_budget(building_id):
    """View 24-month budget for a building"""
    try:
        building_data = queries.get_building_by_id(building_id)
        if not building_data:
            flash('Building not found', 'error')
            return redirect(url_for('home'))

        building = Building.from_dict(building_data)

        # Get budget items
        budget_items_data = queries.get_budget_items(building_id)

        # Generate 24 months starting from current month
        today = datetime.now()
        months = []
        for i in range(24):
            month_date = datetime(today.year, today.month, 1) + timedelta(days=32*i)
            month_date = month_date.replace(day=1)
            months.append(month_date)

        # Organize budget data
        budget_by_category = {}
        for item in budget_items_data:
            category = item['CATEGORY']
            month = item['MONTH_YEAR']
            amount = float(item['AMOUNT'])

            if category not in budget_by_category:
                budget_by_category[category] = {}

            budget_by_category[category][month] = amount

        categories = BudgetItem.CATEGORIES

        return render_template('budget/view.html',
                             building=building,
                             months=months,
                             categories=categories,
                             budget_by_category=budget_by_category)
    except Exception as e:
        logger.error(f"Failed to load budget: {e}", exc_info=True)
        flash('Failed to load budget', 'error')
        return redirect(url_for('view_building', building_id=building_id))


@app.route('/buildings/<building_id>/budget/save', methods=['POST'])
@login_required
def save_budget(building_id):
    """Save budget changes"""
    try:
        building_data = queries.get_building_by_id(building_id)
        if not building_data:
            return jsonify({'success': False, 'message': 'Building not found'}), 404

        # Get budget data from JSON request
        budget_data = request.get_json()

        if not budget_data:
            return jsonify({'success': False, 'message': 'No budget data provided'}), 400

        # Prepare budget items for bulk upsert
        budget_items = []
        for item in budget_data:
            budget_items.append({
                'building_id': building_id,
                'month_year': item['month'],
                'category': item['category'],
                'amount': float(item['amount']),
                'notes': item.get('notes', '')
            })

        # Bulk upsert
        results = queries.bulk_upsert_budget_items(budget_items)

        logger.info(f"Budget saved for building {building_id}: {results}")

        return jsonify({
            'success': True,
            'message': f"Budget saved: {results['success']} items updated",
            'results': results
        })

    except Exception as e:
        logger.error(f"Failed to save budget: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# Document Routes
# ============================================================================

@app.route('/buildings/<building_id>/documents')
@login_required
def view_documents(building_id):
    """List documents for a building"""
    try:
        building_data = queries.get_building_by_id(building_id)
        if not building_data:
            flash('Building not found', 'error')
            return redirect(url_for('home'))

        building = Building.from_dict(building_data)

        # Get documents
        documents_data = queries.get_documents_by_building(building_id)
        documents = [Document.from_dict(d) for d in documents_data]

        # Group by category
        docs_by_category = {}
        for doc in documents:
            if doc.category not in docs_by_category:
                docs_by_category[doc.category] = []
            docs_by_category[doc.category].append(doc)

        return render_template('documents/list.html',
                             building=building,
                             docs_by_category=docs_by_category,
                             categories=Document.CATEGORIES)
    except Exception as e:
        logger.error(f"Failed to load documents: {e}", exc_info=True)
        flash('Failed to load documents', 'error')
        return redirect(url_for('view_building', building_id=building_id))


@app.route('/buildings/<building_id>/documents/upload', methods=['GET', 'POST'])
@login_required
def upload_document(building_id):
    """Upload a document"""
    try:
        building_data = queries.get_building_by_id(building_id)
        if not building_data:
            flash('Building not found', 'error')
            return redirect(url_for('home'))

        building = Building.from_dict(building_data)

        if request.method == 'POST':
            # Check if file was uploaded
            if 'file' not in request.files:
                flash('No file uploaded', 'error')
                return render_template('documents/upload.html',
                                     building=building,
                                     categories=Document.CATEGORIES)

            file = request.files['file']
            category = request.form.get('category', '').strip()

            if file.filename == '':
                flash('No file selected', 'error')
                return render_template('documents/upload.html',
                                     building=building,
                                     categories=Document.CATEGORIES)

            if not category:
                flash('Category is required', 'error')
                return render_template('documents/upload.html',
                                     building=building,
                                     categories=Document.CATEGORIES)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                # Create building-specific folder
                building_folder = os.path.join(app.config['UPLOAD_FOLDER'], building_id)
                os.makedirs(building_folder, exist_ok=True)

                # Save file
                file_path = os.path.join(building_folder, filename)
                file.save(file_path)

                # Get file size
                file_size = os.path.getsize(file_path)

                # Get uploaded by
                uploaded_by = session.get('user', {}).get('email', 'Unknown')

                # Create document record
                document_id = queries.create_document(
                    building_id=building_id,
                    category=category,
                    filename=filename,
                    file_path=file_path,
                    file_size=file_size,
                    uploaded_by=uploaded_by
                )

                logger.info(f"Document uploaded: {filename} (ID: {document_id})")
                flash(f'Successfully uploaded: {filename}', 'success')
                return redirect(url_for('view_documents', building_id=building_id))
            else:
                flash('Invalid file type. Allowed types: pdf, doc, docx, xls, xlsx, txt, png, jpg, jpeg', 'error')

        return render_template('documents/upload.html',
                             building=building,
                             categories=Document.CATEGORIES)
    except Exception as e:
        logger.error(f"Failed to upload document: {e}", exc_info=True)
        flash('Failed to upload document', 'error')
        return redirect(url_for('view_building', building_id=building_id))


@app.route('/documents/<document_id>/download')
@login_required
def download_document(document_id):
    """Download a document"""
    try:
        document_data = queries.get_document_by_id(document_id)
        if not document_data:
            flash('Document not found', 'error')
            return redirect(url_for('home'))

        document = Document.from_dict(document_data)

        if not os.path.exists(document.file_path):
            flash('File not found on server', 'error')
            return redirect(url_for('view_documents', building_id=document.building_id))

        return send_file(document.file_path, as_attachment=True, download_name=document.filename)

    except Exception as e:
        logger.error(f"Failed to download document: {e}", exc_info=True)
        flash('Failed to download document', 'error')
        return redirect(url_for('home'))


@app.route('/documents/<document_id>/delete', methods=['POST'])
@login_required
def delete_document(document_id):
    """Delete a document"""
    try:
        document_data = queries.get_document_by_id(document_id)
        if not document_data:
            flash('Document not found', 'error')
            return redirect(url_for('home'))

        document = Document.from_dict(document_data)
        building_id = document.building_id

        # Delete file from filesystem
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Delete document record
        if queries.delete_document(document_id):
            logger.info(f"Document deleted: {document_id}")
            flash(f'Successfully deleted: {document.filename}', 'success')
        else:
            flash('Failed to delete document', 'error')

        return redirect(url_for('view_documents', building_id=building_id))

    except Exception as e:
        logger.error(f"Failed to delete document: {e}", exc_info=True)
        flash('Failed to delete document', 'error')
        return redirect(url_for('home'))


# ============================================================================
# Shareable Link Route (No Authentication Required)
# ============================================================================

@app.route('/shared/<token>')
def shared_view(token):
    """Public view - no authentication required"""
    try:
        entity_data = queries.get_entity_by_share_token(token)
        if not entity_data:
            return render_template('error.html',
                                 error='Invalid or expired share link',
                                 message='This link may have been revoked or has expired.'), 404

        entity = Entity.from_dict(entity_data)

        # Get buildings
        buildings_data = queries.get_buildings_by_entity(entity.entity_id)
        buildings = [Building.from_dict(b) for b in buildings_data]

        # Get aggregate budget
        budget_data = queries.get_entity_budget(entity.entity_id)

        # Organize budget data
        budget_by_month = {}
        categories = set()

        for item in budget_data:
            month = item['MONTH_YEAR']
            category = item['CATEGORY']
            amount = float(item['TOTAL_AMOUNT'])

            if month not in budget_by_month:
                budget_by_month[month] = {}

            budget_by_month[month][category] = amount
            categories.add(category)

        sorted_months = sorted(budget_by_month.keys())
        sorted_categories = sorted(list(categories))

        return render_template('shared/public_view.html',
                             entity=entity,
                             buildings=buildings,
                             budget_by_month=budget_by_month,
                             months=sorted_months,
                             categories=sorted_categories)

    except Exception as e:
        logger.error(f"Failed to load shared view: {e}", exc_info=True)
        return render_template('error.html',
                             error='Failed to load shared view',
                             message='An error occurred while loading this page.'), 500


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html',
                         error='Page Not Found',
                         message='The page you are looking for does not exist.'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return render_template('error.html',
                         error='Internal Server Error',
                         message='An unexpected error occurred. Please try again later.'), 500


@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large errors"""
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(request.url)


# ============================================================================
# Template Filters
# ============================================================================

@app.template_filter('currency')
def currency_filter(value):
    """Format value as currency"""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


@app.template_filter('month_name')
def month_name_filter(value):
    """Format date as month name and year"""
    try:
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d')
        return value.strftime('%b %Y')
    except (ValueError, AttributeError):
        return str(value)


# ============================================================================
# Run Application
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    logger.info(f"Starting Asset Management Platform on port {port}")
    logger.info(f"Debug mode: {debug}")

    app.run(host='0.0.0.0', port=port, debug=debug)

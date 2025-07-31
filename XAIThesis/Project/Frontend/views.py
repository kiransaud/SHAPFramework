import csv
import logging
import os,json
from django.utils import timezone
from decimal import Decimal,InvalidOperation
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login,logout
from django.urls import reverse
from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from .models import CustomUser,UserRoles
from .utils import generate_email_confirmation_token
from django.contrib.auth.decorators import login_required
import  pandas as pd
import io
import random
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import StudySession, ScenarioResponse

# Configure logger for this module
logger = logging.getLogger(__name__)

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Login successful')
            # Here we render login.html with a redirect_url to be auto-redirected via JS.
            # return render(request, "user_role.html", {
            #     "form": form,
            #     "redirect_url": reverse('home')
            # }
            return redirect('user_role')  # Redirect to user_role view after successful login
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    form.fields['password'].widget.attrs.update({'id': 'id_password'})
    return render(request, "login.html", {"form": form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # The form's save() method sets user.is_active=False
            token = generate_email_confirmation_token(user)
            confirm_url = request.build_absolute_uri(
                reverse('confirm_email', kwargs={'token': token})
            )
            subject = "Confirm Your Email"
            message = (
                f"Hi {user.name},\n\n"
                f"Please click the link below to confirm your email address and activate your account:\n"
                f"{confirm_url}\n\n"
                f"If you did not sign up for an account, please ignore this email."
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            try:
                send_mail(subject, message, from_email, [user.email])
                messages.success(request, "Account created successfully. Please check your email to confirm your account.")
            except Exception as e:
                logger.error("Failed to send email confirmation.", exc_info=True)
                messages.error(request, f"Account created but email confirmation could not be sent. Please contact support. ({e})")
            return redirect('login')
        else:
            # Collect detailed error messages
            error_list = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_list.append(f"{field.capitalize()}: {error}")
            error_message = "Registration failed. " + " ".join(error_list)
            messages.error(request, error_message)
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def confirm_email(request, token):
    try:
        # Use the same salt used in the token generator: 'email_confirmation'
        data = signing.loads(token, salt='email_confirmation', max_age=86400)  # Token valid for 1 day
        user_id = data.get('user_id')
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been activated. You can now log in.")
        else:
            messages.info(request, "Your account is already active.")
    except signing.SignatureExpired:
        messages.error(request, "The confirmation link has expired.")
    except (signing.BadSignature, CustomUser.DoesNotExist):
        messages.error(request, "Invalid confirmation link.")
    return redirect('login')

# @login_required
# def user_role_view(request):
    
#     if not hasattr(request.user, 'user_role') or not request.user.user_role.role:
#         # If not, show an error message and re-render the role selection page
#         messages.error(request, "Please select a role before proceeding.")
#         return render(request, 'user_role.html')  # Adjust template name as needed
    
#     user_role = request.user.user_role.role
#     if user_role == 'DEV':
#         return render(request, 'role/developer.html')
#     elif user_role == 'QA':
#         return render(request, 'role/qa_engineer.html')
#     elif user_role == 'MGR':
#         return render(request, 'role/project_manager.html')
#     elif user_role == 'DOM':
#         return render(request, 'role/domain_expert.html')
#     else:
#         messages.error(request, "Invalid user role.")
#         return redirect('home')

@login_required
def user_role_view(request):
    if request.method == "POST":
        # Get the role value submitted by the form
        selected_role = request.POST.get("role")
        # Validate the selected role
        if not selected_role or selected_role not in ['DEV', 'QA', 'MGR', 'DOM']:
            messages.error(request, "Please select a valid role.")
            return render(request, "user_role.html")
        
        # Record the role: update if exists, or create a new record.
        if hasattr(request.user, "user_role"):
            user_role_obj = request.user.user_role
            user_role_obj.role = selected_role
            user_role_obj.save()
        else:
            UserRoles.objects.create(user=request.user, role=selected_role)
        
        # Render the appropriate role page directly
        if selected_role == 'DEV':
            return render(request, "roles/developer.html")
        elif selected_role == 'QA':
            return render(request, "roles/qa_engineer.html")
        elif selected_role == 'MGR':
            return render(request, "roles/manager.html")
        elif selected_role == 'DOM':
            return render(request, "roles/domain_expert.html")
    
    else:  # GET request
        # If the user already has a role, directly render the corresponding page.
        if hasattr(request.user, "user_role") and request.user.user_role.role:
            selected_role = request.user.user_role.role
            if selected_role == 'DEV':
                return render(request, "roles/developer.html")
            elif selected_role == 'QA':
                return render(request, "roles/qa_engineer.html")
            elif selected_role == 'MGR':
                return render(request, "roles/manager.html")
            elif selected_role == 'DOM':
                return render(request, "roles/domain_expert.html")
        # Otherwise, render the role selection page.
        return render(request, "user_role.html")

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('home')


def training_sustainability(request):
    base_dir = os.path.join('training_data', 'data')
    # Load data files
    summary_df = pd.read_csv(os.path.join(base_dir, 'model_summary.csv'))
    importance_df = pd.read_csv(os.path.join(base_dir, 'model_feature_importances.csv'))
    emission_df = pd.read_csv(os.path.join(base_dir, 'emissions.csv'))
    cm_df = pd.read_csv(os.path.join(base_dir, 'confusion_matrix.csv'))

    # Prepare summary data
    summary = summary_df.set_index('Metric')['Value'].to_dict()
    summary_data = summary_df.to_dict(orient='records')

    # Prepare emissions data
    emissions = emission_df.iloc[-1].to_dict() if not emission_df.empty else {}

    # Process feature importance
    importance_df = importance_df.rename(columns={'Feature': 'feature', 'Gini Importance': 'importance'})
    importance_records = importance_df.sort_values(by='importance', ascending=False).to_dict(orient='records')

    # Process confusion matrix
    cm = {
        'TN': cm_df[(cm_df['actual'] == 0) & (cm_df['predicted'] == 0)]['count'].values[0],
        'FP': cm_df[(cm_df['actual'] == 0) & (cm_df['predicted'] == 1)]['count'].values[0],
        'FN': cm_df[(cm_df['actual'] == 1) & (cm_df['predicted'] == 0)]['count'].values[0],
        'TP': cm_df[(cm_df['actual'] == 1) & (cm_df['predicted'] == 1)]['count'].values[0],
    }
    total = cm['TN'] + cm['FP'] + cm['FN'] + cm['TP']
    accuracy = (cm['TN'] + cm['TP']) / total

    # Prepare classification report
    classification_report = [
        {
            'class_name': 0,
            'precision': summary.get('Precision (0)', 0),
            'recall': summary.get('Recall (0)', 0),
            'f1': summary.get('F1-Score (0)', 0),
            'support': cm['TN'] + cm['FP']
        },
        {
            'class_name': 1,
            'precision': summary.get('Precision (1)', 0),
            'recall': summary.get('Recall (1)', 0),
            'f1': summary.get('F1-Score (1)', 0),
            'support': cm['FN'] + cm['TP']
        }
    ]

    # Confusion matrix data for visualization
    cm_values = [
        {"x": int(row.predicted), "y": int(row.actual), "v": int(row.count)}
        for row in cm_df.itertuples()
    ]

    context = {
        'summary': summary,
        'emissions': emissions,
        'summary_data': summary_data,
        'importance_data': importance_records,
        'feature_labels_json': json.dumps([r['feature'] for r in importance_records]),
        'feature_values_json': json.dumps([r['importance'] for r in importance_records]),
        "cm_values_json": json.dumps(cm_values),
        "cm_max": int(cm_df['count'].max()),
        'classification_report': classification_report,
        'accuracy': accuracy,
        'total_support': total,
        'roc_auc': summary.get('AUC', 0),
    }
    return render(request, 'training.html', context)


logger = logging.getLogger(__name__)


def energy_comparison(request):
    """
    Enhanced energy comparison view with proper validation and error handling
    """
    try:
        # --- Enhanced CSV Loading with Validation ---
        if request.method == 'POST' and request.FILES.get('csv_file'):
            uploaded_file = request.FILES['csv_file']

            # Validate file size (max 5MB)
            if uploaded_file.size > 5 * 1024 * 1024:
                messages.error(request, 'File size too large. Maximum 5MB allowed.')
                return render(request, 'energy_comparison.html', {'error': True})

            # Validate file extension
            if not uploaded_file.name.lower().endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return render(request, 'energy_comparison.html', {'error': True})

            try:
                # Read and decode file
                decoded = uploaded_file.read().decode('utf-8')
                f = io.StringIO(decoded)
                reader = csv.DictReader(f)

                # Validate required columns
                required_columns = {
                    'project_name', 'energy_consumed', 'cpu_energy',
                    'ram_energy', 'gpu_energy', 'duration', 'emissions'
                }

                if not required_columns.issubset(set(reader.fieldnames or [])):
                    missing = required_columns - set(reader.fieldnames or [])
                    messages.error(request, f'Missing required columns: {", ".join(missing)}')
                    return render(request, 'energy_comparison.html', {'error': True})

            except UnicodeDecodeError:
                messages.error(request, 'File encoding error. Please ensure UTF-8 encoding.')
                return render(request, 'energy_comparison.html', {'error': True})
            except Exception as e:
                logger.error(f"CSV processing error: {str(e)}")
                messages.error(request, 'Error processing CSV file.')
                return render(request, 'energy_comparison.html', {'error': True})
        else:
            # Load default static file
            base_dir = os.path.join('emissions', 'data')
            csv_path = os.path.join(base_dir, 'emissions.csv')

            if not os.path.exists(csv_path):
                messages.error(request, 'Default data file not found.')
                return render(request, 'energy_comparison.html', {'error': True})

            f = open(csv_path, newline='', encoding='utf-8')
            reader = csv.DictReader(f)

        # --- Enhanced Data Processing ---
        rows = {}
        required_projects = {'RF_Baseline', 'SHAP_Explanation'}

        try:
            for row_num, r in enumerate(reader, 1):
                try:
                    name = r['project_name'].strip()

                    # Validate and convert numeric fields
                    rows[name] = {
                        'energy': Decimal(str(r['energy_consumed']).strip()),
                        'cpu': Decimal(str(r['cpu_energy']).strip()),
                        'ram': Decimal(str(r['ram_energy']).strip()),
                        'gpu': Decimal(str(r['gpu_energy']).strip()),
                        'duration': Decimal(str(r['duration']).strip()),
                        'emissions': Decimal(str(r['emissions']).strip()),
                    }

                    # Validate positive values
                    for key, value in rows[name].items():
                        if value < 0:
                            messages.error(request, f'Negative value found in row {row_num}, column {key}')
                            return render(request, 'energy_comparison.html', {'error': True})

                except (ValueError, InvalidOperation, KeyError) as e:
                    messages.error(request, f'Invalid data in row {row_num}: {str(e)}')
                    return render(request, 'energy_comparison.html', {'error': True})

        except Exception as e:
            logger.error(f"Data processing error: {str(e)}")
            messages.error(request, 'Error processing data rows.')
            return render(request, 'energy_comparison.html', {'error': True})
        finally:
            # Close file if it was opened (not for uploaded files)
            if request.method != 'POST' or 'csv_file' not in request.FILES:
                f.close()

        # Validate required projects exist
        missing_projects = required_projects - set(rows.keys())
        if missing_projects:
            messages.error(request, f'Missing required projects: {", ".join(missing_projects)}')
            return render(request, 'energy_comparison.html', {'error': True})

        # --- Enhanced Calculations with Zero Division Protection ---
        baseline = rows['RF_Baseline']
        shap = rows['SHAP_Explanation']

        # Core metrics with safety checks
        difference = shap['energy'] - baseline['energy']
        pct_increase = ((shap['energy'] / baseline['energy']) - 1) * 100 if baseline['energy'] > 0 else Decimal(0)
        ratio = shap['energy'] / baseline['energy'] if baseline['energy'] > 0 else Decimal(0)

        # Component differences with safety checks
        def safe_percentage_increase(new_val, old_val):
            return ((new_val / old_val) - 1) * 100 if old_val > 0 else Decimal(0)

        cpu_diff = shap['cpu'] - baseline['cpu']
        cpu_pct_increase = safe_percentage_increase(shap['cpu'], baseline['cpu'])

        ram_diff = shap['ram'] - baseline['ram']
        ram_pct_increase = safe_percentage_increase(shap['ram'], baseline['ram'])

        gpu_diff = shap['gpu'] - baseline['gpu']
        gpu_pct_increase = safe_percentage_increase(shap['gpu'], baseline['gpu'])

        # Duration and efficiency metrics
        duration_ratio = shap['duration'] / baseline['duration'] if baseline['duration'] > 0 else Decimal(0)
        duration_minutes_more = (shap['duration'] - baseline['duration']) / Decimal(60)
        emissions_pct = safe_percentage_increase(shap['emissions'], baseline['emissions'])

        # Efficiency calculations
        eff_baseline = baseline['energy'] / baseline['duration'] if baseline['duration'] > 0 else Decimal(0)
        eff_shap = shap['energy'] / shap['duration'] if shap['duration'] > 0 else Decimal(0)
        eff_pct = abs((eff_shap / eff_baseline - 1) * 100) if eff_baseline > 0 else Decimal(0)
        eff_label = 'better' if eff_shap < eff_baseline else 'worse'

        # Enhanced breakdown with validation
        breakdown_list = []
        for proj in ['RF_Baseline', 'SHAP_Explanation']:
            data = rows[proj]
            total = data['energy']

            breakdown_list.append({
                'name': proj.replace('_', ' '),
                'cpu': float(data['cpu']),
                'ram': float(data['ram']),
                'gpu': float(data['gpu']),
                'total': float(total),
                'cpu_pct': float(data['cpu'] / total * 100) if total > 0 else 0,
                'ram_pct': float(data['ram'] / total * 100) if total > 0 else 0,
                'gpu_pct': float(data['gpu'] / total * 100) if total > 0 else 0,
            })

        # Chart data arrays
        energy_labels = [d['name'] for d in breakdown_list]
        energy_values = [float(baseline['energy']), float(shap['energy'])]
        duration_values = [float(baseline['duration']), float(shap['duration'])]
        emissions_values = [float(baseline['emissions']), float(shap['emissions'])]
        breakdown_names = energy_labels
        breakdown_cpu = [d['cpu'] for d in breakdown_list]
        breakdown_ram = [d['ram'] for d in breakdown_list]
        breakdown_gpu = [d['gpu'] for d in breakdown_list]

        # Enhanced context with metadata
        context = {
            'success': True,
            'data_source': 'uploaded' if request.method == 'POST' and request.FILES.get('csv_file') else 'default',
            'total_projects': len(rows),
            'energy_values': energy_values,
            'comparisonMetrics': {
                'difference': float(difference),
                'pct_increase': float(pct_increase),
                'ratio': float(ratio),
            },
            'component_increases': {
                'cpu_increase': float(cpu_diff),
                'cpu_pct_increase': float(cpu_pct_increase),
                'ram_increase': float(ram_diff),
                'ram_pct_increase': float(ram_pct_increase),
                'gpu_increase': float(gpu_diff),
                'gpu_pct_increase': float(gpu_pct_increase),
            },
            'duration_ratio': float(duration_ratio),
            'duration_minutes_more': float(duration_minutes_more),
            'emissions_pct': float(emissions_pct),
            'eff_pct': float(eff_pct),
            'eff_label': eff_label,
            'breakdownData': breakdown_list,
            'energy_labels': energy_labels,
            'energy_values': energy_values,
            'duration_values': duration_values,
            'emissions_values': emissions_values,
            'breakdown_names': breakdown_names,
            'breakdown_cpu': breakdown_cpu,
            'breakdown_ram': breakdown_ram,
            'breakdown_gpu': breakdown_gpu,
            # Additional metadata
            'raw_data': {
                'baseline': {k: float(v) for k, v in baseline.items()},
                'shap': {k: float(v) for k, v in shap.items()}
            }
        }

        # Add success message for uploaded files
        if request.method == 'POST' and request.FILES.get('csv_file'):
            messages.success(request, f'Successfully processed CSV with {len(rows)} projects.')

        return render(request, 'energy_comparison.html', context)

    except Exception as e:
        logger.error(f"Unexpected error in energy_comparison: {str(e)}")
        messages.error(request, 'An unexpected error occurred while processing your request.')
        return render(request, 'energy_comparison.html', {'error': True})


def export_analysis_data(request):
    """
    API endpoint to export analysis data as JSON
    """
    if request.method == 'GET':
        try:
            # Re-run the analysis to get fresh data
            # This is a simplified version - you might want to cache results
            context = energy_comparison(request).context_data

            export_data = {
                'timestamp': str(timezone.now()),
                'metrics': context.get('comparisonMetrics', {}),
                'component_data': context.get('component_increases', {}),
                'chart_data': {
                    'energy_values': context.get('energy_values', []),
                    'emissions_values': context.get('emissions_values', []),
                    'breakdown_cpu': context.get('breakdown_cpu', []),
                    'breakdown_ram': context.get('breakdown_ram', []),
                    'breakdown_gpu': context.get('breakdown_gpu', []),
                }
            }

            return JsonResponse(export_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def guide_view(request):
    return render(request, 'guide.html')

# study/views.py (just the relevant snippet)

def start_study(request):
    """
    Called when a user first visits /study/.
    - Randomly assign order = 'A_first' or 'B_first'.
    - Create a new StudySession row.
    - Render `study.html` with `session_id` and `order` in context.
    """
    # 1) Randomly pick whether this participant sees Baseline first (A_first)
    #    or SHAP first (B_first).
    order = random.choice(["A_first", "B_first"])

    # 2) Create the StudySession row
    session = StudySession.objects.create(order=order)
    session_id = session.session_id

    # 3) Render the template, passing session_id and order
    return render(request, "study.html", {
        "session_id": session_id,
        "order": order,
    })


@csrf_exempt
def save_response(request):
    """
    Expects a JSON POST with:
      - session_id         (int)
      - scenario_number    (1..6)
      - decision_key       (string)
      - confidence         (int 1..7)
      - time_spent_ms      (int)
    We call update_or_create() so that if the user re‐submits the same scenario,
    we simply overwrite the old row.  The ScenarioResponse.save() method will
    automatically compute `is_correct` using SCENARIO_CORRECT_DECISION.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("This endpoint only accepts POST.")

    try:
        data = json.loads(request.body)
        session_id = int(data["session_id"])
        scenario_number = int(data["scenario_number"])
        decision_key = str(data["decision_key"])
        confidence = int(data["confidence"])
        time_spent_ms = int(data["time_spent_ms"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    session = get_object_or_404(StudySession, session_id=session_id)

    # Create or update the ScenarioResponse row.  .save() will set is_correct automatically.
    ScenarioResponse.objects.update_or_create(
        session=session,
        scenario_number=scenario_number,
        defaults={
            "decision_key": decision_key,
            "confidence": confidence,
            "time_spent_ms": time_spent_ms,
        }
    )
    return JsonResponse({"status": "ok"})


@csrf_exempt
def complete_session(request):
    """
    Called when all 6 scenarios have been saved. Expects JSON POST with:
      - session_id      (int)
      - total_time_ms   (int)
    This will mark StudySession.completed_at and total_time_ms.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    try:
        data = json.loads(request.body)
        session_id    = int(data["session_id"])
        total_time_ms = int(data["total_time_ms"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    session = get_object_or_404(StudySession, session_id=session_id)
    session.completed_at  = timezone.now()
    session.total_time_ms = total_time_ms
    session.save(update_fields=["completed_at", "total_time_ms"])

    return JsonResponse({"status": "session marked complete"})

def study_complete(request, session_id):
    """
    After the frontend has finished all 6 scenarios, you can redirect the user to
    /study_complete/<session_id>/?total_time=<ms> or similar.  This view simply
    looks up the session, computes both blocks’ accuracy, and renders a thank‐you page.
    (Optional, if you want to show accuracy immediately; otherwise you can omit this.)
    """
    session = get_object_or_404(StudySession, session_id=session_id)
    return render(request, "study_complete.html", {
        "session": session,
        "acc_baseline": session.accuracy_baseline(),
        "acc_shap": session.accuracy_shap(),
        "total_time": request.GET.get("total_time"),
    })

@csrf_exempt
def complete_session(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    try:
        data         = json.loads(request.body)
        session_id   = int(data["session_id"])
        total_time_ms = int(data["total_time_ms"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    session = get_object_or_404(StudySession, session_id=session_id)
    session.completed_at    = timezone.now()
    session.total_time_ms   = total_time_ms
    session.save(update_fields=["completed_at", "total_time_ms"])

    return JsonResponse({"status": "session marked complete"})

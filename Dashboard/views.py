from django.shortcuts import render
from .models import Project1Record, Project2Record, ProjectFetchLog

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from django.http import JsonResponse
from Dashboard.models import Project1Record, Project2Record
from collections import defaultdict
import traceback







def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard_view')
    return render(request, 'sankalp_dashboard_main/login.html')



def dashboard_view(request):
  return render(request, 'sankalp_dashboard_main/dashboard.html')


def profile_view(request):
  return render(request, 'sankalp_dashboard_main/profile.html')




#  Handle Login Request (POST)
# -------------------------------
@csrf_exempt  # remove after you add CSRF token in production
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            password = data.get('password')

            # Authenticate using email
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'message': 'Login successful'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid email or password'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)



# Logout API
# -------------------------------
def logout_user(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out successfully'})



##################### Dashboard####################


#######Total adelivery Count #############


def count_total_deliveries(request):
    """
    Return total number of deliveries from both projects:
    (Live Born + Still Born / IUD)
    Excludes test records (no data_access_group assigned).
    """
    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")
    live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
    live_fields = ['baby1_status', 'baby2_status', 'baby3_status']

    def count_live_babies(qs):
        return sum(
            qs.filter(**{f"{field}__in": live_statuses}).count()
            for field in live_fields
        )

    live_p1 = count_live_babies(Project1Record.objects.exclude(exclude_dag_filter))
    live_p2 = count_live_babies(Project2Record.objects.exclude(exclude_dag_filter))
    total_live = live_p1 + live_p2

    still_status = 'Still Born / IUD'
    still_fields = ['baby1_status', 'baby2_status', 'baby3_status']

    def count_still_born(qs):
        return sum(
            qs.filter(**{f"{field}__exact": still_status}).count()
            for field in still_fields
        )

    still_p1 = count_still_born(Project1Record.objects.exclude(exclude_dag_filter))
    still_p2 = count_still_born(Project2Record.objects.exclude(exclude_dag_filter))
    total_still = still_p1 + still_p2

    total_deliveries = total_live + total_still

    return JsonResponse({
        "project1_live": live_p1,
        "project2_live": live_p2,
        "project1_stillborn": still_p1,
        "project2_stillborn": still_p2,
        "total_live": total_live,
        "total_stillborn": total_still,
        "total_deliveries": total_deliveries
    })

######### total delivery dagwise############




def count_total_deliveries_dag(request):
    """
     DAG-wise total deliveries (Live Born + Still Born/IUD)
    from both Project1Record and Project2Record.
    Counts per baby field (not per record)
    """

    try:
        live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
        still_status = 'Still Born / IUD'
        fields = ['baby1_status', 'baby2_status', 'baby3_status']
        dag_counts = defaultdict(int)

        #  Querysets excluding unassigned DAGs
        project1_records = Project1Record.objects.exclude(
            Q(data_access_group__isnull=True) | Q(data_access_group__exact="")
        )
        project2_records = Project2Record.objects.exclude(
            Q(data_access_group__isnull=True) | Q(data_access_group__exact="")
        )

        def process_record(record):
            """Count babies per record"""
            dag_name = (getattr(record, "data_access_group", "") or "").strip().lower()

            count = 0
            for f in fields:
                status = getattr(record, f, "")
                if status in live_statuses or status == still_status:
                    count += 1

            if count > 0 and dag_name:
                dag_counts[dag_name] += count

        for rec in project1_records:
            process_record(rec)

        for rec in project2_records:
            process_record(rec)

        normalized_dag_counts = defaultdict(int)
        name_mapping = {
            "mursidabad": "Murshidabad",
            "murshidabad": "Murshidabad",
            "varansi": "Varanasi",
            "ambala": "Ambala",
            "haridwar": "Haridwar",
            "unnao": "Unnao",
            "purnea": "Purnea",
            "khargone": "Khargone",
            "adilabad": "Adilabad",
            "koppal": "Koppal",
            "dungarpur": "Dungarpur",
        }

        for dag, count in dag_counts.items():
            normalized_name = name_mapping.get(dag, dag.capitalize())
            normalized_dag_counts[normalized_name] += count

        # Sort descending by count
        sorted_dag_counts = sorted(
            normalized_dag_counts.items(),
            key=lambda x: -x[1]
        )

        overall_total = sum(normalized_dag_counts.values())

        result = [{"dag": dag, "total_deliveries": count} for dag, count in sorted_dag_counts]

        return JsonResponse({
            "dag_counts": result,
            "overall_total": overall_total
        })

    except Exception as e:
        print(" Error in count_total_deliveries_dag:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)

def count_baby_status_live(request):
    """
    Return JSON response with total occurrences of
    'Live Born (Well)' and 'Live Born (Sick)'
    """

    statuses = ['Live Born (Well)', 'Live Born (Sick)']

    # Project 1 - exclude empty or null DAGs
    project1_qs = Project1Record.objects.exclude(
        Q(data_access_group__isnull=True) | Q(data_access_group__exact="")
    )

    count_project1_total = sum(
        project1_qs.filter(**{f"{field}__exact": status}).count()
        for field in ['baby1_status', 'baby2_status', 'baby3_status']
        for status in statuses
    )

    # Project 2 - exclude empty or null DAGs
    project2_qs = Project2Record.objects.exclude(
        Q(data_access_group__isnull=True) | Q(data_access_group__exact="")
    )

    count_project2_total = sum(
        project2_qs.filter(**{f"{field}__exact": status}).count()
        for field in ['baby1_status', 'baby2_status', 'baby3_status']
        for status in statuses
    )

    total_count = count_project1_total + count_project2_total

    return JsonResponse({
        "project1_count": count_project1_total,
        "project2_count": count_project2_total,
        "total_count": total_count
    })


def baby_stillborn_count_view(request):
    """
    Return total count of babies where status == 'Still Born / IUD'
    from both Project1Record and Project2Record.
    """

    status_value = 'Still Born / IUD'
    fields = ['baby1_status', 'baby2_status', 'baby3_status']

    def count_babies(queryset):
        return sum(
            queryset.filter(**{f"{field}__exact": status_value}).count()
            for field in fields
        )

    # Count for both projects
    count_project1 = count_babies(Project1Record.objects.all())
    count_project2 = count_babies(Project2Record.objects.all())

    total_count = count_project1 + count_project2

    print("Project1 - Still Born babies:", count_project1)
    print("Project2 - Still Born babies:", count_project2)
    print("Total Still Born babies:", total_count)

    return JsonResponse({
        "project1_count": count_project1,
        "project2_count": count_project2,
        "total_count": total_count
    })


########still born dagwise########




def stillborn_dag_count_view(request):
    """
    Return DAG-wise count of records where any baby status == 'Still Born / IUD'
    from both Project1Record and Project2Record, excluding 0-count DAGs.
    """

    status_value = 'Still Born / IUD'
    fields = ['baby1_status', 'baby2_status', 'baby3_status']

    def get_dag_counts(queryset):
        dag_counts = {}
        dags = queryset.values_list('data_access_group', flat=True).distinct()
        for dag in dags:
            if not dag:
                continue  # skip None or blank DAGs
            qs_dag = queryset.filter(data_access_group=dag)
            count_total = sum(
                qs_dag.filter(**{f"{field}__exact": status_value}).count()
                for field in fields
            )
            dag_counts[dag.strip()] = count_total
        return dag_counts

    # DAG counts for both projects
    project1_counts = get_dag_counts(Project1Record.objects.all())
    project2_counts = get_dag_counts(Project2Record.objects.all())

    # Combine counts
    combined_counts = {}
    all_dags = set(list(project1_counts.keys()) + list(project2_counts.keys()))
    for dag in all_dags:
        combined_counts[dag] = project1_counts.get(dag, 0) + project2_counts.get(dag, 0)
    combined_counts = {dag: count for dag, count in combined_counts.items() if count > 0}

    overall_total = sum(combined_counts.values())

    # print("Project1 DAG counts:", project1_counts)
    # print("Project2 DAG counts:", project2_counts)
    # print("Filtered Combined DAG counts:", combined_counts)
    # print("Overall total Still Born / IUD:", overall_total)

    return JsonResponse({
        "project1_counts": project1_counts,
        "project2_counts": project2_counts,
        "combined_counts": combined_counts,
        "overall_total": overall_total
    })




def count_live_born_by_dag(request):
    """
    Return JSON response with Live Born (Well + Sick) counts grouped by
    Data Access Group for both Project1Record and Project2Record,
    normalizing DAG names and ignoring 'No DAG'.
    """

    statuses = ['Live Born (Well)', 'Live Born (Sick)']

    # Mapping normalized DAG names to canonical names
    DAG_NAME_MAP = {
        "varanasi": "Varanasi",
        "varansi": "Varanasi",
        "mursidabad": "Murshidabad",
        "murshidabad": "Murshidabad",
        "ambala": "Ambala",
        "Ambala": "Ambala",
        # add more mappings if needed
    }

    def get_dag_counts(queryset):
        dag_counts = {}
        dags = queryset.values_list('data_access_group', flat=True).distinct()
        for dag in dags:
            if not dag:
                continue  # skip None or empty DAG
            normalized = dag.strip().lower()
            canonical = DAG_NAME_MAP.get(normalized, dag.strip())
            qs_dag = queryset.filter(data_access_group=dag)
            count_total = sum(
                qs_dag.filter(**{f"{field}__exact": status}).count()
                for field in ['baby1_status', 'baby2_status', 'baby3_status']
                for status in statuses
            )
            dag_counts[canonical] = dag_counts.get(canonical, 0) + count_total
        return dag_counts

    # Project 1 DAG counts
    project1_counts = get_dag_counts(Project1Record.objects.all())
    # Project 2 DAG counts
    project2_counts = get_dag_counts(Project2Record.objects.all())

    # Total combined DAG counts
    combined_counts = {}
    all_dags = set(list(project1_counts.keys()) + list(project2_counts.keys()))
    for dag in all_dags:
        combined_counts[dag] = project1_counts.get(dag, 0) + project2_counts.get(dag, 0)

    # Overall total
    overall_total = sum(combined_counts.values())

    return JsonResponse({
        "project1_counts": project1_counts,
        "project2_counts": project2_counts,
        "combined_counts": combined_counts,
        "overall_total": overall_total
    })



#########Neontal Death#########



def count_dead_calls(request):
    
    project1_fields = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]
    project2_fields = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]

    # Build OR queries safely
    q1 = Q()
    for f in project1_fields:
        q1 |= Q(**{f"{f}__icontains": "Dead"})
    project1_count = Project1Record.objects.filter(q1).count()

    q2 = Q() 
    for f in project2_fields:
        q2 |= Q(**{f"{f}__icontains": "Dead"})
    project2_count = Project2Record.objects.filter(q2).count()

    total_dead = project1_count + project2_count

    print("Project1 Dead total:", project1_count)
    print("Project2 Dead total:", project2_count)
    print("Total Dead:", total_dead)

    return JsonResponse({
        "project1_dead": project1_count,
        "project2_dead": project2_count,
        "total_dead": total_dead,
    })


######neontal death dagwise  ############

def count_dead_calls_dag(request):
    """
    Return DAG-wise count of babies where d29_baby_current_status_bX contains 'Dead'
    (from both Project1Record and Project2Record).
    Merges DAG names that differ only by case or spacing.
    """

    project1_fields = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]
    project2_fields = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]


    DAG_NAME_MAP = {
        "varansi": "Varanasi",
        "varanasi": "Varanasi",
        "mursidabad": "Murshidabad",
        "murshidabad": "Murshidabad",
        "ambala": "Ambala",
    }

    try:
        def build_dead_q(fields):
            """Helper: Build OR query for any field containing 'Dead'."""
            q = Q()
            for f in fields:
                q |= Q(**{f"{f}__icontains": "Dead"})
            return q

        dag_counts = defaultdict(int)

        def normalize_dag_name(raw_name):
            if not raw_name:
                return "Unknown"
            name = raw_name.strip().lower()
            return DAG_NAME_MAP.get(name, name.title())

        project1_qs = Project1Record.objects.filter(build_dead_q(project1_fields))
        print("Project1 Dead Records Count:", project1_qs.count())

        for rec in project1_qs:
            dag_name = normalize_dag_name(getattr(rec, "data_access_group", None))
            dag_counts[dag_name] += 1

        project2_qs = Project2Record.objects.filter(build_dead_q(project2_fields))
        print("Project2 Dead Records Count:", project2_qs.count())

        for rec in project2_qs:
            dag_name = normalize_dag_name(getattr(rec, "data_access_group", None))
            dag_counts[dag_name] += 1

        print("DAG-wise Dead Counts (normalized):", dict(dag_counts))
        overall_total = sum(dag_counts.values())
        print("Overall Total Dead Calls:", overall_total)

        result = [
            {"dag": dag, "dead_count": count}
            for dag, count in sorted(dag_counts.items(), key=lambda x: x[0])
        ]

        return JsonResponse({
            "dag_counts": result,
            "overall_total": overall_total
        })

    except Exception as e:
        print("Error in count_dead_calls_dag:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)
    

#######day_29 followup    



def count_connected_calls(request):
    """
    Returns total count of 'Connected' calls across d29_call_status_b1/b2/b3
    for both Project1Record and Project2Record.
    """

    # Day 29 Call Status fields
    project1_fields = [
        "d29_call_status_b1",
        "d29_call_status_b2",
        "d29_call_status_b3",
    ]
    project2_fields = [
        "d29_call_status_b1",
        "d29_call_status_b2",
        "d29_call_status_b3",
    ]

    #  Build dynamic OR filter for "Connected"
    def build_connected_q(fields):
        q = Q()
        for f in fields:
            q |= Q(**{f"{f}__iexact": "Connected"})  # exact match (case-insensitive)
        return q


    project1_count = Project1Record.objects.filter(build_connected_q(project1_fields)).count()

    project2_count = Project2Record.objects.filter(build_connected_q(project2_fields)).count()

    total_connected = project1_count + project2_count

    print("Project1 Connected Calls:", project1_count)
    print("Project2 Connected Calls:", project2_count)
    print("Overall Total Connected Calls:", total_connected)

    return JsonResponse({
        "project1_connected": project1_count,
        "project2_connected": project2_count,
        "total_connected": total_connected
    })

######day29 connect dagwise#############


def count_connected_calls_dag(request):
    """
    Return DAG-wise count of records where any d29_call_status_bX == 'Connected'
    from both Project1Record and Project2Record.
    DAG names are normalized and combined.
    """

    project1_fields = [
        "d29_call_status_b1",
        "d29_call_status_b2",
        "d29_call_status_b3",
    ]
    project2_fields = [
        "d29_call_status_b1",
        "d29_call_status_b2",
        "d29_call_status_b3",
    ]

    DAG_NAME_MAP = {
        "varansi": "Varanasi",
        "varanasi": "Varanasi",
        "mursidabad": "Murshidabad",
        "murshidabad": "Murshidabad",
        "ambala": "Ambala",
    }

    try:
        def build_connected_q(fields):
            """Helper: Build OR query for fields containing 'Connected'"""
            q = Q()
            for f in fields:
                q |= Q(**{f"{f}__iexact": "Connected"})
            return q

        def normalize_dag_name(raw_name):
            """Helper: Normalize DAG names (fix case, spacing, typos)"""
            if not raw_name:
                return "Unknown"
            name = raw_name.strip().lower()
            return DAG_NAME_MAP.get(name, name.title())

        dag_counts = defaultdict(int)

        project1_qs = Project1Record.objects.filter(build_connected_q(project1_fields))
        print("Project1 Connected Records:", project1_qs.count())

        for rec in project1_qs:
            dag_name = normalize_dag_name(getattr(rec, "data_access_group", None))
            dag_counts[dag_name] += 1

        project2_qs = Project2Record.objects.filter(build_connected_q(project2_fields))
        print("Project2 Connected Records:", project2_qs.count())

        for rec in project2_qs:
            dag_name = normalize_dag_name(getattr(rec, "data_access_group", None))
            dag_counts[dag_name] += 1
        print("DAG-wise Connected Counts:", dict(dag_counts))
        overall_total = sum(dag_counts.values())
        print("Overall Total Connected Calls:", overall_total)

        result = [
            {"dag": dag, "connected_count": count}
            for dag, count in sorted(dag_counts.items(), key=lambda x: x[0])
        ]

        return JsonResponse({
            "dag_counts": result,
            "overall_total": overall_total
        })

    except Exception as e:
        print("Error in count_connected_calls_dag:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)
    


###########SBR##############################3


def stillbirth_rate_view(request):
    """
    Calculate and return the Stillbirth Rate (SBR):
    (Still Born / IUD ÷ Total Deliveries) × 1000
    Excludes records with no data_access_group (test/unassigned).
    """

    # Exclude test/unassigned DAGs
    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")
    still_status = 'Still Born / IUD'
    fields = ['baby1_status', 'baby2_status', 'baby3_status']

    def count_still_born(qs):
        return sum(
            qs.filter(**{f"{field}__exact": still_status}).count()
            for field in fields
        )

    still_p1 = count_still_born(Project1Record.objects.exclude(exclude_dag_filter))
    still_p2 = count_still_born(Project2Record.objects.exclude(exclude_dag_filter))
    total_still = still_p1 + still_p2

    live_statuses = ['Live Born (Well)', 'Live Born (Sick)']

    def count_live_babies(qs):
        return sum(
            qs.filter(**{f"{field}__in": live_statuses}).count()
            for field in fields
        )

    live_p1 = count_live_babies(Project1Record.objects.exclude(exclude_dag_filter))
    live_p2 = count_live_babies(Project2Record.objects.exclude(exclude_dag_filter))
    total_live = live_p1 + live_p2

    total_deliveries = total_live + total_still
    sbr = (total_still / total_deliveries * 1000) if total_deliveries > 0 else 0

    return JsonResponse({
        "project1_stillborn": still_p1,
        "project2_stillborn": still_p2,
        "total_stillborn": total_still,
        "total_deliveries": total_deliveries,
        "stillbirth_rate_per_1000": round(sbr, 2)
    })



#########SBR dagwise################3

def stillbirth_rate_dag_view(request):
    """
    Return DAG-wise Stillbirth Rate (SBR):
    (Still Born / IUD ÷ Total Deliveries) × 1000
     DAG records.
    """
    try:
        exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")
        live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
        still_status = 'Still Born / IUD'
        fields = ['baby1_status', 'baby2_status', 'baby3_status']

        project1_records = Project1Record.objects.exclude(exclude_dag_filter)
        project2_records = Project2Record.objects.exclude(exclude_dag_filter)

        dag_data = defaultdict(lambda: {"stillborn": 0, "total": 0})

        def process_record(record):
            dag_name = (getattr(record, "data_access_group", "") or "").strip().lower()
            if not dag_name:
                return
            for f in fields:
                status = getattr(record, f, "")
                if status in live_statuses:
                    dag_data[dag_name]["total"] += 1
                elif status == still_status:
                    dag_data[dag_name]["stillborn"] += 1
                    dag_data[dag_name]["total"] += 1

        for rec in project1_records:
            process_record(rec)
        for rec in project2_records:
            process_record(rec)

        # Normalize DAG names and merge duplicates
        name_mapping = {
            "mursidabad": "Murshidabad",
            "murshidabad": "Murshidabad",
            "varansi": "Varanasi",
            "ambala": "Ambala",
            "haridwar": "Haridwar",
            "unnao": "Unnao",
            "purnea": "Purnea",
            "khargone": "Khargone",
            "adilabad": "Adilabad",
            "koppal": "Koppal",
            "dungarpur": "Dungarpur",
        }

        merged = defaultdict(lambda: {"stillborn": 0, "total": 0})
        for dag, vals in dag_data.items():
            dag_clean = name_mapping.get(dag, dag.capitalize())
            merged[dag_clean]["stillborn"] += vals["stillborn"]
            merged[dag_clean]["total"] += vals["total"]

        results = []
        for dag, vals in merged.items():
            total = vals["total"]
            stillborn = vals["stillborn"]
            sbr = (stillborn / total * 1000) if total > 0 else 0
            results.append({
                "dag": dag,
                "sbr_per_1000": round(sbr, 2)
            })

        results.sort(key=lambda x: -x["sbr_per_1000"])

        total_still = sum(v["stillborn"] for v in merged.values())
        total_deliveries = sum(v["total"] for v in merged.values())
        overall_sbr = (total_still / total_deliveries * 1000) if total_deliveries > 0 else 0

        # ✅ Return JSON structure matching your JS expectations
        return JsonResponse({
            "dag_wise_sbr": results,
            "overall": {
                "total_stillborn": total_still,
                "total_deliveries": total_deliveries,
                "overall_sbr_per_1000": round(overall_sbr, 2)
            }
        })

    except Exception:
        print(" Error in stillbirth_rate_dag_view:", traceback.format_exc())
    return JsonResponse({"error": "Server error in SBR DAG view"}, status=500)



####################NMR############################



def neonatal_mortality_rate_view(request):
    """
    Calculate and return Neonatal Mortality Rate (NRM):
    (Total Dead ÷ Total Deliveries) × 1000
    Excludes unassigned/test DAG records.
    """

    # Exclude test/unassigned DAGs
    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")
    project1_fields = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]
    project2_fields = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]

    q1 = Q()
    for f in project1_fields:
        q1 |= Q(**{f"{f}__icontains": "Dead"})
    project1_count = Project1Record.objects.exclude(exclude_dag_filter).filter(q1).count()

    q2 = Q()
    for f in project2_fields:
        q2 |= Q(**{f"{f}__icontains": "Dead"})
    project2_count = Project2Record.objects.exclude(exclude_dag_filter).filter(q2).count()

    total_dead = project1_count + project2_count
    live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
    still_status = 'Still Born / IUD'
    fields = ['baby1_status', 'baby2_status', 'baby3_status']

    def count_status(qs, statuses):
        return sum(qs.filter(**{f"{field}__in": statuses}).count() for field in fields)

    def count_exact(qs, status):
        return sum(qs.filter(**{f"{field}__exact": status}).count() for field in fields)

    p1 = Project1Record.objects.exclude(exclude_dag_filter)
    p2 = Project2Record.objects.exclude(exclude_dag_filter)

    total_live = count_status(p1, live_statuses) + count_status(p2, live_statuses)
    total_still = count_exact(p1, still_status) + count_exact(p2, still_status)
    total_deliveries = total_live + total_still

    nmr = (total_dead / total_deliveries * 1000) if total_deliveries > 0 else 0

    return JsonResponse({
        "project1_dead": project1_count,
        "project2_dead": project2_count,
        "total_dead": total_dead,
        "total_deliveries": total_deliveries,
        "neonatal_mortality_rate_per_1000": round(nmr, 2)
    })



#############NMR DAG_WISE######################



def neonatal_mortality_rate_dag_view(request):
    """
    Return DAG-wise Neonatal Mortality Rate (NMR):
    (Total Dead ÷ Total Deliveries) × 1000
    from both Project1Record and Project2Record.
    Excludes unassigned/test DAG records.
    """

    try:
        exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")
        live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
        still_status = 'Still Born / IUD'
        dead_fields = ['d29_baby_current_status_b1', 'd29_baby_current_status_b2', 'd29_baby_current_status_b3']
        birth_fields = ['baby1_status', 'baby2_status', 'baby3_status']

        project1_records = Project1Record.objects.exclude(exclude_dag_filter)
        project2_records = Project2Record.objects.exclude(exclude_dag_filter)

        dag_data = defaultdict(lambda: {"dead": 0, "deliveries": 0})

        def process_record(record):
            dag_name = (getattr(record, "data_access_group", "") or "").strip().lower()
            if not dag_name:
                return

            # Count live + still for total deliveries
            for f in birth_fields:
                status = getattr(record, f, "")
                if status in live_statuses or status == still_status:
                    dag_data[dag_name]["deliveries"] += 1

            # Count deaths from day 29 baby current status
            for f in dead_fields:
                status = getattr(record, f, "")
                if status and "dead" in status.lower():
                    dag_data[dag_name]["dead"] += 1

        for rec in project1_records:
            process_record(rec)
        for rec in project2_records:
            process_record(rec)
        name_mapping = {
            "mursidabad": "Murshidabad",
            "murshidabad": "Murshidabad",
            "varansi": "Varanasi",
            "ambala": "Ambala",
            "haridwar": "Haridwar",
            "unnao": "Unnao",
            "purnea": "Purnea",
            "khargone": "Khargone",
            "adilabad": "Adilabad",
            "koppal": "Koppal",
            "dungarpur": "Dungarpur",
        }

        merged_data = defaultdict(lambda: {"dead": 0, "deliveries": 0})
        for dag, vals in dag_data.items():
            dag_clean = name_mapping.get(dag, dag.capitalize())
            merged_data[dag_clean]["dead"] += vals["dead"]
            merged_data[dag_clean]["deliveries"] += vals["deliveries"]
        results = []
        for dag, vals in merged_data.items():
            dead = vals["dead"]
            deliveries = vals["deliveries"]
            nmr = (dead / deliveries * 1000) if deliveries > 0 else 0
            results.append({
                "dag": dag,
                "nmr_per_1000": round(nmr, 2),
                "total_dead": dead,
                "total_deliveries": deliveries
            })
        results.sort(key=lambda x: -x["nmr_per_1000"])

        total_dead = sum(v["dead"] for v in merged_data.values())
        total_deliveries = sum(v["deliveries"] for v in merged_data.values())
        overall_nmr = (total_dead / total_deliveries * 1000) if total_deliveries > 0 else 0

        return JsonResponse({
            "dag_wise_nmr": results,
            "overall": {
                "total_dead": total_dead,
                "total_deliveries": total_deliveries,
                "overall_nmr_per_1000": round(overall_nmr, 2)
            }
        })

    except Exception:
        print(" Error in neonatal_mortality_rate_dag_view:", traceback.format_exc())
        return JsonResponse({"error": "Server error in NMR DAG view"}, status=500)
    



#####SBR+NMR#############


def sbr_nmr_combined_view(request):
    """
    Returns combined Stillbirth Rate (SBR) and Neonatal Mortality Rate (NMR):
    """

    try:
       
        exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")

        live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
        still_status = 'Still Born / IUD'
        dead_fields = [
            'd29_baby_current_status_b1',
            'd29_baby_current_status_b2',
            'd29_baby_current_status_b3'
        ]
        birth_fields = ['baby1_status', 'baby2_status', 'baby3_status']

        project1 = Project1Record.objects.exclude(exclude_dag_filter)
        project2 = Project2Record.objects.exclude(exclude_dag_filter)

        def count_stillbirths(qs):
            return sum(qs.filter(**{f"{f}__exact": still_status}).count() for f in birth_fields)

        still_p1 = count_stillbirths(project1)
        still_p2 = count_stillbirths(project2)
        total_still = still_p1 + still_p2
        def count_live(qs):
            return sum(qs.filter(**{f"{f}__in": live_statuses}).count() for f in birth_fields)

        total_live = count_live(project1) + count_live(project2)
        total_deliveries = total_live + total_still

        def count_deaths(qs):
            q = Q()
            for f in dead_fields:
                q |= Q(**{f"{f}__icontains": "Dead"})
            return qs.filter(q).count()

        dead_p1 = count_deaths(project1)
        dead_p2 = count_deaths(project2)
        total_dead = dead_p1 + dead_p2

        sbr = (total_still / total_deliveries * 1000) if total_deliveries > 0 else 0
        nmr = (total_dead / total_deliveries * 1000) if total_deliveries > 0 else 0

        return JsonResponse({
            "total_deliveries": total_deliveries,
            "total_stillbirths": total_still,
            "total_dead": total_dead,
            "sbr_per_1000": round(sbr, 2),
            "nmr_per_1000": round(nmr, 2),
            "combined_total_per_1000": round(sbr + nmr, 2)  
        })

    except Exception:
        print(" Error in sbr_nmr_combined_view:", traceback.format_exc())
        return JsonResponse({"error": "Server error in combined SBR+NMR view"}, status=500)
    





#########SBR+NMR dagwise###############


def sbr_nmr_combined_dag_view(request):
    """
    Returns DAG-wise combined SBR + NMR per 1000 deliveries:
    """

    try:
       
        exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")

        live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
        still_status = 'Still Born / IUD'
        dead_fields = [
            'd29_baby_current_status_b1',
            'd29_baby_current_status_b2',
            'd29_baby_current_status_b3'
        ]
        birth_fields = ['baby1_status', 'baby2_status', 'baby3_status']

        project1_records = Project1Record.objects.exclude(exclude_dag_filter)
        project2_records = Project2Record.objects.exclude(exclude_dag_filter)

        dag_data = defaultdict(lambda: {"stillborn": 0, "dead": 0, "deliveries": 0})

        def process_record(record):
            dag_name = (getattr(record, "data_access_group", "") or "").strip().lower()
            if not dag_name:
                return

            for f in birth_fields:
                status = getattr(record, f, "")
                if status in live_statuses or status == still_status:
                    dag_data[dag_name]["deliveries"] += 1
                if status == still_status:
                    dag_data[dag_name]["stillborn"] += 1

        
            for f in dead_fields:
                status = getattr(record, f, "")
                if status and "dead" in str(status).lower():
                    dag_data[dag_name]["dead"] += 1

        for rec in project1_records:
            process_record(rec)
        for rec in project2_records:
            process_record(rec)

        name_mapping = {
            "mursidabad": "Murshidabad",
            "murshidabad": "Murshidabad",
            "varansi": "Varanasi",
            "ambala": "Ambala",
            "haridwar": "Haridwar",
            "unnao": "Unnao",
            "purnea": "Purnea",
            "khargone": "Khargone",
            "adilabad": "Adilabad",
            "koppal": "Koppal",
            "dungarpur": "Dungarpur",
        }

        merged_data = defaultdict(lambda: {"stillborn": 0, "dead": 0, "deliveries": 0})
        for dag, vals in dag_data.items():
            dag_clean = name_mapping.get(dag, dag.capitalize())
            merged_data[dag_clean]["stillborn"] += vals["stillborn"]
            merged_data[dag_clean]["dead"] += vals["dead"]
            merged_data[dag_clean]["deliveries"] += vals["deliveries"]

        results = []
        for dag, vals in merged_data.items():
            stillborn = vals["stillborn"]
            dead = vals["dead"]
            deliveries = vals["deliveries"]

            sbr = (stillborn / deliveries * 1000) if deliveries > 0 else 0
            nmr = (dead / deliveries * 1000) if deliveries > 0 else 0
            combined = sbr + nmr

            results.append({
                "dag": dag,
                "sbr_per_1000": round(sbr, 2),
                "nmr_per_1000": round(nmr, 2),
                "combined_per_1000": round(combined, 2),
                "total_deliveries": deliveries
            })

        results.sort(key=lambda x: -x["combined_per_1000"])
        total_still = sum(v["stillborn"] for v in merged_data.values())
        total_dead = sum(v["dead"] for v in merged_data.values())
        total_deliveries = sum(v["deliveries"] for v in merged_data.values())

        overall_sbr = (total_still / total_deliveries * 1000) if total_deliveries > 0 else 0
        overall_nmr = (total_dead / total_deliveries * 1000) if total_deliveries > 0 else 0
        overall_combined = overall_sbr + overall_nmr
        return JsonResponse({
            "dag_wise_combined": results,
            "overall": {
                "total_deliveries": total_deliveries,
                "total_stillborn": total_still,
                "total_dead": total_dead,
                "overall_sbr_per_1000": round(overall_sbr, 2),
                "overall_nmr_per_1000": round(overall_nmr, 2),
                "overall_combined_per_1000": round(overall_combined, 2)
            }
        })

    except Exception:
        print(" Error in sbr_nmr_combined_dag_view:", traceback.format_exc())
        return JsonResponse({"error": "Server error in SBR+NMR DAG view"}, status=500)



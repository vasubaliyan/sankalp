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

from django.http import HttpResponse
import threading






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

##########3handel data refrsh######

# views.py


# from Dashboard.fetch_project2 import fetch_and_save_project1
# from Dashboard.fetch_project1 import fetch_and_save_project2



# def refresh_data(request):
#     """
#     Background thread se Project1 + Project2 fetch karega.
#     Frontend ko turant response dega.
#     """
#     threading.Thread(target=fetch_and_save_project1).start()
#     threading.Thread(target=fetch_and_save_project2).start()
#     return HttpResponse("✅ Fetch started! Data will update shortly.")


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



#######performance dashboard#######day_29 complete############



def chart_view(request):
    return render(request, "sankalp_dashboard_main/chart.html")



def count_day29_followup_combined(request):
    """
    Returns combined Day-29 follow-up (Connected vs Incomplete)
    Compared against total live births.
    """

    dag = request.GET.get("dag", None)
    LIVE_BIRTH_STATUSES = ['Live Born (Well)', 'Live Born (Sick)']
    CONNECTED_STATUS = 'Connected'

    def get_live_births(model):
        qs = model.objects.exclude(Q(data_access_group__isnull=True) | Q(data_access_group__exact=""))
        if dag and dag.lower() != "all":
            qs = qs.filter(data_access_group__iexact=dag)
        fields = ["baby1_status", "baby2_status", "baby3_status"]
        count = sum(qs.filter(**{f"{f}__in": LIVE_BIRTH_STATUSES}).count() for f in fields)
        return count

    live_births_count = get_live_births(Project1Record) + get_live_births(Project2Record)

    def get_connected_calls(model):
        qs = model.objects.exclude(Q(data_access_group__isnull=True) | Q(data_access_group__exact=""))
        if dag and dag.lower() != "all":
            qs = qs.filter(data_access_group__iexact=dag)
        fields = ["d29_call_status_b1", "d29_call_status_b2", "d29_call_status_b3"]
        count = sum(qs.filter(**{f"{f}__iexact": CONNECTED_STATUS}).count() for f in fields)
        return count

    connected_count = get_connected_calls(Project1Record) + get_connected_calls(Project2Record)
    not_connected = live_births_count - connected_count if live_births_count > connected_count else 0

    percent_connected = round((connected_count / live_births_count * 100), 2) if live_births_count else 0
    percent_incomplete = round(100 - percent_connected, 2)
    coverage_vs_livebirths = percent_connected

    dags1 = list(Project1Record.objects.exclude(Q(data_access_group__isnull=True) | Q(data_access_group__exact=""))
                 .values_list("data_access_group", flat=True).distinct())
    dags2 = list(Project2Record.objects.exclude(Q(data_access_group__isnull=True) | Q(data_access_group__exact=""))
                 .values_list("data_access_group", flat=True).distinct())
    all_dags = sorted(list(set(dags1 + dags2)))

    return JsonResponse({
        "live_births_total": live_births_count,
        "day29_followup": {
            "connected": connected_count,
            "incomplete": not_connected,
            "percent_connected": percent_connected,
            "percent_incomplete": percent_incomplete,
            "coverage_vs_livebirths_percent": coverage_vs_livebirths
        },
        "available_dags": all_dags,
        "selected_dag": dag or "All"
    })


#######Birth weight available no of delivery#################3


def count_birthweight_availability(request):
    """
    Returns DAG-wise (or total) number of deliveries 
    (Live Born + Still Born / IUD)
    and how many of those have birthweight available,
    from both Project1 and Project2.
    Merges DAGs with spelling variations (e.g., Varansi→Varanasi).
    """

    raw_dag = request.GET.get("dag", None)
    dag = (raw_dag or "").strip().rstrip("/").lower()  # normalized input

    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")

    live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
    still_status = 'Still Born / IUD'

    status_fields = ['baby1_status', 'baby2_status', 'baby3_status']
    birthweight_fields = ['baby1_birthweight', 'baby2_birthweight', 'baby3_birthweight']

    # ✅ Spelling correction / DAG mapping
    DAG_NORMALIZATION = {
        "varansi": "varanasi",
        "mursidabad": "murshidabad",
        "ambala ": "ambala",  # just in case of space
    }

    def normalize_dag(value):
        if not value:
            return None
        v = str(value).strip().rstrip("/").lower()
        return DAG_NORMALIZATION.get(v, v)

    def get_queryset(model):
        qs = model.objects.exclude(exclude_dag_filter)
        if dag and dag != "all":
            normalized = normalize_dag(dag)
            # filter for all variants that map to this DAG
            dag_variants = [k for k, v in DAG_NORMALIZATION.items() if v == normalized]
            dag_variants.append(normalized)
            qs = qs.filter(data_access_group__in=dag_variants)
        return qs

    def count_deliveries_with_birthweight(model):
        qs = get_queryset(model)
        total = with_bw = 0

        for record in qs.values(*status_fields, *birthweight_fields):
            for i in range(1, 4):
                status = record.get(f"baby{i}_status")
                birthweight = record.get(f"baby{i}_birthweight")

                if status in live_statuses + [still_status]:
                    total += 1
                    if birthweight and str(birthweight).strip() != "":
                        with_bw += 1
        return total, with_bw

    # ✅ Apply to both projects
    p1_total, p1_with_bw = count_deliveries_with_birthweight(Project1Record)
    p2_total, p2_with_bw = count_deliveries_with_birthweight(Project2Record)

    total_deliveries = p1_total + p2_total
    total_with_birthweight = p1_with_bw + p2_with_bw
    total_missing_birthweight = total_deliveries - total_with_birthweight

    percent_with_bw = round((total_with_birthweight / total_deliveries * 100), 2) if total_deliveries else 0
    percent_missing_bw = round(100 - percent_with_bw, 2)

    # ✅ Normalize + deduplicate DAGs for dropdown
    dags1 = [normalize_dag(x) for x in Project1Record.objects.exclude(exclude_dag_filter)
             .values_list("data_access_group", flat=True).distinct()]
    dags2 = [normalize_dag(x) for x in Project2Record.objects.exclude(exclude_dag_filter)
             .values_list("data_access_group", flat=True).distinct()]
    all_dags = sorted(list({d.capitalize() for d in dags1 + dags2 if d}))

    selected_display_dag = normalize_dag(raw_dag).capitalize() if dag and dag != "all" else "All"

    return JsonResponse({
        "selected_dag": selected_display_dag,
        "project1": {
            "total_deliveries": p1_total,
            "with_birthweight": p1_with_bw,
            "missing_birthweight": p1_total - p1_with_bw,
        },
        "project2": {
            "total_deliveries": p2_total,
            "with_birthweight": p2_with_bw,
            "missing_birthweight": p2_total - p2_with_bw,
        },
        "combined": {
            "total_deliveries": total_deliveries,
            "with_birthweight": total_with_birthweight,
            "missing_birthweight": total_missing_birthweight,
            "percent_with_birthweight": percent_with_bw,
            "percent_missing_birthweight": percent_missing_bw,
        },
        "available_dags": all_dags
    })


###########delivery location place of birth available ##############


def count_delivery_location_availability(request):
    """
    Returns combined (Project1 + Project2) count of delivery_location
    availability vs missing based on TOTAL DELIVERIES (Live + Still Born / IUD),
    baby-level matching with total deliveries (e.g. 152,805).
    """

    dag = request.GET.get("dag", None)

    # Fields
    status_fields = ["baby1_status", "baby2_status", "baby3_status"]
    delivery_location_field = "delivery_location"

    live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
    still_status = 'Still Born / IUD'
    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")

    # DAG filter helper
    def get_queryset(model):
        qs = model.objects.exclude(exclude_dag_filter)
        if dag and dag.lower() != "all":
            qs = qs.filter(data_access_group__iexact=dag)
        return qs

    # 🧮 Baby-level counting (same as total deliveries logic)
    def count_locations(model):
        qs = get_queryset(model)
        available = 0
        missing = 0
        total = 0

        for record in qs.values(*status_fields, delivery_location_field):
            delivery_location = record.get(delivery_location_field)

            for i in range(1, 4):  # baby1, baby2, baby3
                status = record.get(f"baby{i}_status")

                # Only count valid deliveries (live/still)
                if status in live_statuses + [still_status]:
                    total += 1
                    if delivery_location and str(delivery_location).strip() != "":
                        available += 1
                    else:
                        missing += 1

        return available, missing, total

    # 🔹 Project-wise counts
    p1_available, p1_missing, p1_total = count_locations(Project1Record)
    p2_available, p2_missing, p2_total = count_locations(Project2Record)

    # 🔹 Combine results
    total_available = p1_available + p2_available
    total_missing = p1_missing + p2_missing
    total_deliveries = p1_total + p2_total  

    percent_available = round((total_available / total_deliveries * 100), 2) if total_deliveries else 0
    percent_missing = round(100 - percent_available, 2)

    # 🔹 Distinct DAGs for dropdown
    dags1 = list(Project1Record.objects.exclude(exclude_dag_filter)
                 .values_list("data_access_group", flat=True).distinct())
    dags2 = list(Project2Record.objects.exclude(exclude_dag_filter)
                 .values_list("data_access_group", flat=True).distinct())
    all_dags = sorted(list(set(dags1 + dags2)))

    # 🔹 Final JSON
    return JsonResponse({
        "selected_dag": dag or "All",
        "delivery_location": {
            "available": total_available,
            "not_available": total_missing,
            "total": total_deliveries,
            "percent_available": percent_available,
            "percent_missing": percent_missing
        },
        "available_dags": all_dags
    })



############## neontal death have place of death ############


def count_death_place_availability(request):
    """
    Return JSON with:
    - total deaths (from both projects)
    - how many have place of death available (any of b1/b2/b3)
    - how many missing/not available
    Includes both count and percentage.
    Supports optional ?dag=<dag_name>
    """

    dag = request.GET.get("dag", None)
    # ✅ if dag is 'All' or empty, don't apply filter
    if not dag or dag.lower() == "all":
        dag_filter = None
    else:
        dag_filter = dag.strip().lower()

    project1_status_fields = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]
    project2_status_fields = project1_status_fields.copy()

    place_fields = [
        "d29_baby_death_place_b1",
        "d29_baby_death_place_b2",
        "d29_baby_death_place_b3",
    ]

    def process_project(model, status_fields, place_fields, dag_filter=None):
        q = Q()
        for f in status_fields:
            q |= Q(**{f"{f}__icontains": "Dead"})

        qs = model.objects.filter(q)
        if dag_filter:
            qs = qs.filter(data_access_group__iexact=dag_filter)

        total_deaths = 0
        place_available = 0

        for rec in qs:
            for i, sf in enumerate(status_fields):
                status = getattr(rec, sf, None)
                if status and "Dead" in status:
                    total_deaths += 1
                    pf = place_fields[i]
                    val = getattr(rec, pf, None)
                    if val and val.strip():
                        place_available += 1

        return total_deaths, place_available, total_deaths - place_available

    # 🔹 Combine both projects
    p1_total, p1_avail, p1_missing = process_project(Project1Record, project1_status_fields, place_fields, dag_filter)
    p2_total, p2_avail, p2_missing = process_project(Project2Record, project2_status_fields, place_fields, dag_filter)

    total = p1_total + p2_total
    available = p1_avail + p2_avail
    missing = p1_missing + p2_missing

    avail_pct = round((available / total) * 100, 1) if total else 0
    missing_pct = round((missing / total) * 100, 1) if total else 0

    return JsonResponse({
        "dag": dag if dag else "Overall",
        "combined": {
            "total": total,
            "available": available,
            "missing": missing,
            "available_pct": avail_pct,
            "missing_pct": missing_pct,
        }
    })

def count_death_date_availability(request):
    """
    Return JSON with:
    - total deaths (from both projects)
    - how many have date of death available (any of b1/b2/b3)
    - how many missing/not available
    Optional ?dag=<dag_name>
    """

    dag = request.GET.get("dag", None)
    # ✅ if dag is 'All' or empty, show overall data
    if not dag or dag.lower() == "all":
        dag_filter = None
    else:
        dag_filter = dag.strip().lower()

    project1_status_fields = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]
    project2_status_fields = project1_status_fields.copy()

    date_fields = [
        "d29_baby_death_date_b1",
        "d29_baby_death_date_b2",
        "d29_baby_death_date_b3",
    ]

    def process_project(model, status_fields, date_fields, dag_filter=None):
        q = Q()
        for f in status_fields:
            q |= Q(**{f"{f}__icontains": "Dead"})

        qs = model.objects.filter(q)
        if dag_filter:
            qs = qs.filter(data_access_group__iexact=dag_filter)

        total_deaths = 0
        date_available = 0

        for rec in qs:
            for i, sf in enumerate(status_fields):
                status = getattr(rec, sf, None)
                if status and "Dead" in status:
                    total_deaths += 1
                    df = date_fields[i]
                    val = getattr(rec, df, None)
                    if val and val.strip():
                        date_available += 1

        return total_deaths, date_available, total_deaths - date_available

    # 🔹 Combine both projects
    p1_total, p1_avail, p1_missing = process_project(Project1Record, project1_status_fields, date_fields, dag_filter)
    p2_total, p2_avail, p2_missing = process_project(Project2Record, project2_status_fields, date_fields, dag_filter)

    total = p1_total + p2_total
    available = p1_avail + p2_avail
    missing = p1_missing + p2_missing

    avail_pct = round((available / total) * 100, 1) if total else 0
    missing_pct = round((missing / total) * 100, 1) if total else 0

    return JsonResponse({
        "dag": dag if dag else "Overall",
        "combined": {
            "total": total,
            "available": available,
            "missing": missing,
            "available_pct": avail_pct,
            "missing_pct": missing_pct,
        }
    })


##########livebirth having gender########

def count_livebirth_gender_availability(request):
    """
    Return JSON with:
    - total live births (from both projects)
    - how many have baby gender (sex) available
    - how many missing/not available
    Supports ?dag=<dag_name>
    """

    dag = request.GET.get("dag", None)
    dag_filter = None if not dag or dag.lower() == "all" else dag.strip()

    # Status fields for live births
    live_statuses = ["Live Born (Well)", "Live Born (Sick)"]
    status_fields = ["baby1_status", "baby2_status", "baby3_status"]
    gender_fields = ["baby1_sex", "baby2_sex", "baby3_sex"]

    def process_project(model, dag_filter=None):
        qs = model.objects.all()
        if dag_filter:
            # 🔹 normalize case-insensitive match properly
            qs = qs.filter(data_access_group__iexact=dag_filter)

        total_live = 0
        gender_available = 0

        for rec in qs:
            for i, sf in enumerate(status_fields):
                status = getattr(rec, sf, None)
                if status in live_statuses:
                    total_live += 1
                    gf = gender_fields[i]
                    gender = getattr(rec, gf, None)
                    if gender and gender.strip():
                        gender_available += 1

        gender_missing = total_live - gender_available
        return total_live, gender_available, gender_missing

    # 🔹 Process both projects
    p1_total, p1_avail, p1_missing = process_project(Project1Record, dag_filter)
    p2_total, p2_avail, p2_missing = process_project(Project2Record, dag_filter)

    # 🔹 Combine results
    total = p1_total + p2_total
    available = p1_avail + p2_avail
    missing = p1_missing + p2_missing

    avail_pct = round((available / total) * 100, 1) if total else 0
    missing_pct = round((missing / total) * 100, 1) if total else 0

    # ✅ Add available DAGs (for dropdown)
    dags = (
        list(
            Project1Record.objects.exclude(data_access_group__isnull=True)
            .exclude(data_access_group__exact="")
            .values_list("data_access_group", flat=True)
            .distinct()
        )
        + list(
            Project2Record.objects.exclude(data_access_group__isnull=True)
            .exclude(data_access_group__exact="")
            .values_list("data_access_group", flat=True)
            .distinct()
        )
    )
    dags = sorted(set(dags))

    return JsonResponse({
        "dag": dag if dag else "Overall",
        "available_dags": dags,
        "combined": {
            "total": total,
            "available": available,
            "missing": missing,
            "available_pct": avail_pct,
            "missing_pct": missing_pct,
        },
    })

import traceback

def count_dead_gender_availability(request):
    try:
        dag = request.GET.get("dag", None)
        dag_filter = None if not dag or dag.lower() == "all" else dag.strip().lower()

        status_fields = [
            "d29_baby_current_status_b1",
            "d29_baby_current_status_b2",
            "d29_baby_current_status_b3",
        ]
        gender_fields = [
            "baby1_sex",
            "baby2_sex",
            "baby3_sex",
        ]

        def process_project(model, dag_filter=None):
            q = Q()
            for f in status_fields:
                q |= Q(**{f"{f}__icontains": "Dead"})
            qs = model.objects.filter(q)
            if dag_filter:
                qs = qs.filter(data_access_group__iexact=dag_filter)

            total_dead = 0
            gender_available = 0

            for rec in qs:
                for i, sf in enumerate(status_fields):
                    status = getattr(rec, sf, None)
                    if status and "Dead" in status:
                        total_dead += 1
                        gf = gender_fields[i]
                        gender = getattr(rec, gf, None)
                        if gender and gender.strip():
                            gender_available += 1

            gender_missing = total_dead - gender_available
            return total_dead, gender_available, gender_missing

        p1_total, p1_avail, p1_missing = process_project(Project1Record, dag_filter)
        p2_total, p2_avail, p2_missing = process_project(Project2Record, dag_filter)

        total = p1_total + p2_total
        available = p1_avail + p2_avail
        missing = p1_missing + p2_missing

        avail_pct = round((available / total) * 100, 1) if total else 0
        missing_pct = round((missing / total) * 100, 1) if total else 0

        return JsonResponse({
            "dag": dag if dag else "Overall",
            "combined": {
                "total": total,
                "available": available,
                "missing": missing,
                "available_pct": avail_pct,
                "missing_pct": missing_pct,
            },
        })

    except Exception:
        print("❌ Error in count_dead_gender_availability:", traceback.format_exc())
        return JsonResponse({"error": "Internal Server Error"}, status=500)
    


###########causew of death###########



def count_death_cause_availability(request):
    """
    Returns JSON:
    - total deaths (from both projects)
    - how many have cause of death available
    - how many missing
    Supports ?dag=<dag_name>
    """

    try:
        dag = request.GET.get("dag", None)
        dag_filter = None if not dag or dag.lower() == "all" else dag.strip().lower()

        # status fields for death identification
        status_fields = [
            "d29_baby_current_status_b1",
            "d29_baby_current_status_b2",
            "d29_baby_current_status_b3",
        ]

        # cause of death checkbox fields
        cause_fields = [
            [f"q17_cause_of_death_d29_b1___{i}" for i in range(1, 11)],
            [f"q17_cause_of_death_d29_b2___{i}" for i in range(1, 11)],
            [f"q17_cause_of_death_d29_b3___{i}" for i in range(1, 11)],
        ]

        def process_project(model, dag_filter=None):
            q = Q()
            for f in status_fields:
                q |= Q(**{f"{f}__icontains": "Dead"})
            qs = model.objects.filter(q)
            if dag_filter:
                qs = qs.filter(data_access_group__iexact=dag_filter)

            total_deaths = 0
            cause_available = 0

            for rec in qs:
                for i, sf in enumerate(status_fields):
                    status = getattr(rec, sf, None)
                    if status and "Dead" in status:
                        total_deaths += 1

                        # check if any cause checkbox is filled for this baby
                        cause_list = cause_fields[i]
                        if any(
                            getattr(rec, cf, None) and str(getattr(rec, cf)).strip()
                            for cf in cause_list
                        ):
                            cause_available += 1

            cause_missing = total_deaths - cause_available
            return total_deaths, cause_available, cause_missing

        # Process both projects
        p1_total, p1_avail, p1_missing = process_project(Project1Record, dag_filter)
        p2_total, p2_avail, p2_missing = process_project(Project2Record, dag_filter)

        total = p1_total + p2_total
        available = p1_avail + p2_avail
        missing = p1_missing + p2_missing

        avail_pct = round((available / total) * 100, 1) if total else 0
        missing_pct = round((missing / total) * 100, 1) if total else 0

        return JsonResponse({
            "dag": dag if dag else "Overall",
            "combined": {
                "total": total,
                "available": available,
                "missing": missing,
                "available_pct": avail_pct,
                "missing_pct": missing_pct,
            },
        })

    except Exception:
        print("❌ Error in count_cause_of_death_availability:", traceback.format_exc())
        return JsonResponse({"error": "Internal Server Error"}, status=500)
    

###########outcome dash#############
 
# dashboard/views.py


def outcome_dashboard(request):
    return render(request, "sankalp_dashboard_main/outcome_dashboard.html")




def count_delivery_location_place(request):
    """
    Returns count of delivery_location availability and breakdown
    (only Public, Private, Home, On the way — excludes 'Other').
    """

    dag = request.GET.get("dag", None)

    status_fields = ["baby1_status", "baby2_status", "baby3_status"]
    delivery_location_field = "delivery_location"

    live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
    still_status = 'Still Born / IUD'
    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")

    def get_queryset(model):
        qs = model.objects.exclude(exclude_dag_filter)
        if dag and dag.lower() != "all":
            qs = qs.filter(data_access_group__iexact=dag)
        return qs

    def count_locations(model):
        qs = get_queryset(model)
        available = 0
        total = 0
        breakdown = {
            "Public health facility": 0,
            "Private health facility": 0,
            "Home": 0,
            "On the way": 0
        }

        valid_places = breakdown.keys()

        for record in qs.values(*status_fields, delivery_location_field):
            delivery_location = record.get(delivery_location_field)

            for i in range(1, 4):
                status = record.get(f"baby{i}_status")
                if status in live_statuses + [still_status]:
                    total += 1
                    if delivery_location and str(delivery_location).strip() != "":
                        available += 1
                        loc = str(delivery_location).strip()
                        if loc in valid_places:
                            breakdown[loc] += 1
                        # ignore others (no "Other" count)
        return available, total, breakdown

    # 🔹 Combine both projects
    p1_available, p1_total, p1_breakdown = count_locations(Project1Record)
    p2_available, p2_total, p2_breakdown = count_locations(Project2Record)

    total_available = p1_available + p2_available
    total_deliveries = p1_total + p2_total  

    total_breakdown = {
        key: p1_breakdown.get(key, 0) + p2_breakdown.get(key, 0)
        for key in set(p1_breakdown) | set(p2_breakdown)
    }

    percent_available = round((total_available / total_deliveries * 100), 2) if total_deliveries else 0

    return JsonResponse({
        "selected_dag": dag or "All",
        "delivery_location": {
            "available": total_available,
            "total": total_deliveries,
            "percent_available": percent_available,
            "breakdown": total_breakdown
        }
    })



#####birthweight cat########
# 🟩 Dashboard HTML view
def outcome_dashboard(request):
    return render(request, "outcome_dashboard.html")

def count_birthweight_category(request):
    """
    Returns combined (Project1 + Project2) count of available birthweights
    categorized as:
      <1000g, 1000–1499g, 1500–2499g, ≥2500g
    """
    dag = request.GET.get("dag", None)

    birthweight_fields = ["baby1_birthweight", "baby2_birthweight", "baby3_birthweight"]
    status_fields = ["baby1_status", "baby2_status", "baby3_status"]

    live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
    still_status = 'Still Born / IUD'
    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")

    def get_queryset(model):
        qs = model.objects.exclude(exclude_dag_filter)
        if dag and dag.lower() != "all":
            qs = qs.filter(data_access_group__iexact=dag)
        return qs

    def count_birthweight(model):
        qs = get_queryset(model)
        total = available = missing = 0
        categories = {"<1000": 0, "1000-1499": 0, "1500-2499": 0, "≥2500": 0}

        for record in qs.values(*status_fields, *birthweight_fields):
            for i in range(1, 4):
                status = record.get(f"baby{i}_status")
                bw = record.get(f"baby{i}_birthweight")

                if status in live_statuses + [still_status]:
                    total += 1
                    if bw and str(bw).strip() != "":
                        try:
                            bw_val = float(bw)
                            available += 1
                            if bw_val < 1000:
                                categories["<1000"] += 1
                            elif 1000 <= bw_val < 1500:
                                categories["1000-1499"] += 1
                            elif 1500 <= bw_val < 2500:
                                categories["1500-2499"] += 1
                            else:
                                categories["≥2500"] += 1
                        except ValueError:
                            missing += 1
                    else:
                        missing += 1
        return available, missing, total, categories

    # 🔹 Combine both project models
    p1_available, p1_missing, p1_total, p1_cat = count_birthweight(Project1Record)
    p2_available, p2_missing, p2_total, p2_cat = count_birthweight(Project2Record)

    total_available = p1_available + p2_available
    total_missing = p1_missing + p2_missing
    total_deliveries = p1_total + p2_total

    combined = {k: p1_cat.get(k, 0) + p2_cat.get(k, 0) for k in p1_cat}
    percent_available = round((total_available / total_deliveries * 100), 2) if total_deliveries else 0
    percent_missing = round(100 - percent_available, 2)

    return JsonResponse({
        "birthweight": {
            "available": total_available,
            "not_available": total_missing,
            "total": total_deliveries,
            "percent_available": percent_available,
            "percent_missing": percent_missing,
            "categories": combined
        }
    })


#####3neontal death by birthcategory



def count_birthweight_category_for_dead_calls(request):
    """
    Returns combined (Project1 + Project2) count of babies whose
    d29_baby_current_status_bX contains 'Dead', categorized by birthweight:
      <1000, 1000–1499, 1500–2499, ≥2500
    """

    dag = request.GET.get("dag", None)

    # ✅ Death fields (status fields from D29 form)
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

    # ✅ Birthweight fields (same across both)
    birthweight_fields = [
        "baby1_birthweight",
        "baby2_birthweight",
        "baby3_birthweight",
    ]

    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")

    # Helper: Apply DAG filter
    def get_queryset(model):
        qs = model.objects.exclude(exclude_dag_filter)
        if dag and dag.lower() != "all":
            qs = qs.filter(data_access_group__iexact=dag)
        return qs

    # 🧮 Core counting logic
    def count_dead_birthweights(model, status_fields):
        qs = get_queryset(model)

        total_dead = 0
        available = 0

        categories = {
            "<1000": 0,
            "1000-1499": 0,
            "1500-2499": 0,
            "≥2500": 0
        }

        for record in qs.values(*status_fields, *birthweight_fields):
            for i in range(1, 4):
                status = str(record.get(f"d29_baby_current_status_b{i}") or "").strip()
                bw = record.get(f"baby{i}_birthweight")

                # ✅ Only "Dead" babies
                if "dead" in status.lower():
                    total_dead += 1
                    if bw and str(bw).strip() != "":
                        try:
                            bw_val = float(bw)
                            available += 1
                            if bw_val < 1000:
                                categories["<1000"] += 1
                            elif 1000 <= bw_val < 1500:
                                categories["1000-1499"] += 1
                            elif 1500 <= bw_val < 2500:
                                categories["1500-2499"] += 1
                            else:
                                categories["≥2500"] += 1
                        except ValueError:
                            pass

        return total_dead, available, categories

    # 🔹 Project-wise counts
    p1_dead, p1_avail, p1_cats = count_dead_birthweights(Project1Record, project1_fields)
    p2_dead, p2_avail, p2_cats = count_dead_birthweights(Project2Record, project2_fields)

    # 🔹 Combine totals
    total_dead = p1_dead + p2_dead
    total_available = p1_avail + p2_avail
    combined_cats = {
        key: p1_cats.get(key, 0) + p2_cats.get(key, 0)
        for key in set(p1_cats) | set(p2_cats)
    }

    percent_available = round((total_available / total_dead * 100), 2) if total_dead else 0

    return JsonResponse({
        "selected_dag": dag or "All",
        "birthweight_deaths": {
            "total_dead": total_dead,
            "available_birthweight": total_available,
            "percent_available": percent_available,
            "categories": combined_cats
        }
    })

#####place of death category

def count_place_of_death_for_dead_calls(request):
    """
    Returns combined (Project1 + Project2) count of babies with status == 'Dead',
    categorized by place of death:
      'Public health facility', 'Private health facility', 'Home', 'On the way'
    """

    dag = request.GET.get("dag", None)

    # ✅ Status fields
    status_fields = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]

    # ✅ Place of death fields
    place_fields = [
        "d29_baby_death_place_b1_d14_d7",
        "d29_baby_death_place_b2_d14_d7",
        "d29_baby_death_place_b3_d14_d7",
    ]

    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")

    def get_queryset(model):
        qs = model.objects.exclude(exclude_dag_filter)
        if dag and dag.lower() != "all":
            qs = qs.filter(data_access_group__iexact=dag)
        return qs

    # 🧮 Count logic
    def count_places(model):
        qs = get_queryset(model)

        total_dead = 0
        available = 0
        breakdown = {
            "Public health facility": 0,
            "Private health facility": 0,
            "Home": 0,
            "On the way": 0,
            "Other / Missing": 0
        }

        for record in qs.values(*status_fields, *place_fields):
            for i in range(1, 4):
                status = str(record.get(f"d29_baby_current_status_b{i}") or "").strip()
                place = str(record.get(f"d29_baby_death_place_b{i}_d14_d7") or "").strip()

                # ✅ Check only dead babies
                if "dead" in status.lower():
                    total_dead += 1
                    if place and place.lower() not in ["", "unknown", "nan"]:
                        available += 1
                        if place in breakdown:
                            breakdown[place] += 1
                        else:
                            breakdown["Other / Missing"] += 1
                    else:
                        breakdown["Other / Missing"] += 1

        return total_dead, available, breakdown

    # 🔹 Project-wise
    p1_total, p1_available, p1_breakdown = count_places(Project1Record)
    p2_total, p2_available, p2_breakdown = count_places(Project2Record)

    # 🔹 Combine totals
    total_dead = p1_total + p2_total
    total_available = p1_available + p2_available

    combined_breakdown = {
        key: p1_breakdown.get(key, 0) + p2_breakdown.get(key, 0)
        for key in set(p1_breakdown) | set(p2_breakdown)
    }

    percent_available = round((total_available / total_dead * 100), 2) if total_dead else 0

    # 🔹 DAG list
    dags1 = list(Project1Record.objects.exclude(exclude_dag_filter)
                 .values_list("data_access_group", flat=True).distinct())
    dags2 = list(Project2Record.objects.exclude(exclude_dag_filter)
                 .values_list("data_access_group", flat=True).distinct())
    all_dags = sorted(list(set(dags1 + dags2)))

    # 🔹 JSON Response
    return JsonResponse({
        "selected_dag": dag or "All",
        "place_of_death": {
            "total_dead": total_dead,
            "available": total_available,
            "percent_available": percent_available,
            "breakdown": combined_breakdown
        },
        "available_dags": all_dags
    })

#####death with gender category


def count_dead_gender_availabilitys(request):
    """
    Returns (Project1 + Project2) count of babies where any d29_baby_current_status_bX contains 'Dead',
    along with availability of gender and breakdown by gender category:
      'Male', 'Female', 'Ambiguous', 'Unknown'
    """

    try:
        dag = request.GET.get("dag", None)
        dag_filter = None if not dag or dag.lower() == "all" else dag.strip().lower()

        # ✅ Status & Gender fields
        status_fields = [
            "d29_baby_current_status_b1",
            "d29_baby_current_status_b2",
            "d29_baby_current_status_b3",
        ]
        gender_fields = [
            "baby1_sex",
            "baby2_sex",
            "baby3_sex",
        ]

        #  Process per project
        def process_project(model, dag_filter=None):
            q = Q()
            for f in status_fields:
                q |= Q(**{f"{f}__icontains": "Dead"})
            qs = model.objects.filter(q)
            if dag_filter:
                qs = qs.filter(data_access_group__iexact=dag_filter)

            total_dead = 0
            gender_available = 0
            gender_missing = 0

            breakdown = {
                "Male": 0,
                "Female": 0,
                "Ambiguous": 0,
                "Unknown": 0
            }

            for rec in qs:
                for i in range(3):
                    status = getattr(rec, status_fields[i], None)
                    if status and "dead" in status.lower():
                        total_dead += 1
                        gender = getattr(rec, gender_fields[i], None)
                        if gender and gender.strip():
                            gender_available += 1
                            g = gender.strip().title()  # Normalize casing
                            if g in breakdown:
                                breakdown[g] += 1
                            else:
                                breakdown["Unknown"] += 1
                        else:
                            gender_missing += 1

            return total_dead, gender_available, gender_missing, breakdown

        # 🔹 Combine Project1 + Project2
        p1_total, p1_avail, p1_missing, p1_breakdown = process_project(Project1Record, dag_filter)
        p2_total, p2_avail, p2_missing, p2_breakdown = process_project(Project2Record, dag_filter)

        total = p1_total + p2_total
        available = p1_avail + p2_avail
        missing = p1_missing + p2_missing

        combined_breakdown = {
            key: p1_breakdown.get(key, 0) + p2_breakdown.get(key, 0)
            for key in set(p1_breakdown) | set(p2_breakdown)
        }

        avail_pct = round((available / total) * 100, 1) if total else 0
        missing_pct = round((missing / total) * 100, 1) if total else 0

        return JsonResponse({
            "dag": dag if dag else "Overall",
            "combined": {
                "total": total,
                "available": available,
                "missing": missing,
                "available_pct": avail_pct,
                "missing_pct": missing_pct,
                "breakdown": combined_breakdown
            },
        })

    except Exception:
        print("❌ Error in count_dead_gender_availability:", traceback.format_exc())
        return JsonResponse({"error": "Internal Server Error"}, status=500)


#########livebirth gender distr




def count_livebirth_gender_availabilityes(request):
    """
    Returns (Project1 + Project2) count of live births
    with gender availability and breakdown by:
      'Male', 'Female', 'Ambiguous', 'Unknown'
    Supports ?dag=<dag_name>
    """

    dag = request.GET.get("dag", None)
    dag_filter = None if not dag or dag.lower() == "all" else dag.strip()

    # ✅ Statuses considered "Live Birth"
    live_statuses = ["Live Born (Well)", "Live Born (Sick)"]

    # ✅ Fields
    status_fields = ["baby1_status", "baby2_status", "baby3_status"]
    gender_fields = ["baby1_sex", "baby2_sex", "baby3_sex"]

    # 🧮 Per project processor
    def process_project(model, dag_filter=None):
        qs = model.objects.all()
        if dag_filter:
            qs = qs.filter(data_access_group__iexact=dag_filter)

        total_live = 0
        gender_available = 0
        gender_missing = 0

        breakdown = {
            "Male": 0,
            "Female": 0,
            "Ambiguous": 0,
            "Unknown": 0
        }

        for rec in qs:
            for i in range(3):
                status = getattr(rec, status_fields[i], None)
                if status in live_statuses:
                    total_live += 1
                    gender = getattr(rec, gender_fields[i], None)
                    if gender and gender.strip():
                        gender_available += 1
                        g = gender.strip().title()  # Normalize casing
                        if g in breakdown:
                            breakdown[g] += 1
                        else:
                            breakdown["Unknown"] += 1
                    else:
                        gender_missing += 1

        return total_live, gender_available, gender_missing, breakdown

    # 🔹 Project-wise counts
    p1_total, p1_avail, p1_missing, p1_breakdown = process_project(Project1Record, dag_filter)
    p2_total, p2_avail, p2_missing, p2_breakdown = process_project(Project2Record, dag_filter)

    # 🔹 Combine totals
    total = p1_total + p2_total
    available = p1_avail + p2_avail
    missing = p1_missing + p2_missing

    combined_breakdown = {
        key: p1_breakdown.get(key, 0) + p2_breakdown.get(key, 0)
        for key in set(p1_breakdown) | set(p2_breakdown)
    }

    avail_pct = round((available / total) * 100, 1) if total else 0
    missing_pct = round((missing / total) * 100, 1) if total else 0

    # 🔹 Distinct DAGs (for dropdown)
    dags = (
        list(
            Project1Record.objects.exclude(data_access_group__isnull=True)
            .exclude(data_access_group__exact="")
            .values_list("data_access_group", flat=True)
            .distinct()
        )
        + list(
            Project2Record.objects.exclude(data_access_group__isnull=True)
            .exclude(data_access_group__exact="")
            .values_list("data_access_group", flat=True)
            .distinct()
        )
    )
    dags = sorted(set(dags))

    # 🔹 Final JSON
    return JsonResponse({
        "dag": dag if dag else "Overall",
        "available_dags": dags,
        "combined": {
            "total": total,
            "available": available,
            "missing": missing,
            "available_pct": avail_pct,
            "missing_pct": missing_pct,
            "breakdown": combined_breakdown
        },
    })


##########GA available###########



def count_total_deliveriess(request):
    """
    Returns total deliveries (Live + Still/IUD)
    and how many have gestational age info (available + not available).
    Works even if data_access_group not present.
    """

    dag = request.GET.get("dag", "").strip()

    # 🔹 check if each model actually has data_access_group
    p1_fields = [f.name for f in Project1Record._meta.get_fields()]
    p2_fields = [f.name for f in Project2Record._meta.get_fields()]

    valid_filter_p1 = Q()
    valid_filter_p2 = Q()

    if "data_access_group" in p1_fields:
        valid_filter_p1 &= ~Q(data_access_group__isnull=True) & ~Q(data_access_group__exact="")
        if dag and dag.lower() != "all":
            valid_filter_p1 &= Q(data_access_group__iexact=dag)

    if "data_access_group" in p2_fields:
        valid_filter_p2 &= ~Q(data_access_group__isnull=True) & ~Q(data_access_group__exact="")
        if dag and dag.lower() != "all":
            valid_filter_p2 &= Q(data_access_group__iexact=dag)

    # 🔹 delivery status logic
    live_statuses = ["Live Born (Well)", "Live Born (Sick)"]
    still_status = "Still Born / IUD"
    status_fields = ["baby1_status", "baby2_status", "baby3_status"]

    def count_live(qs):
        return sum(qs.filter(**{f"{f}__in": live_statuses}).count() for f in status_fields)

    def count_still(qs):
        return sum(qs.filter(**{f"{f}__exact": still_status}).count() for f in status_fields)

    # 🔹 apply filters safely
    p1 = Project1Record.objects.filter(valid_filter_p1)
    p2 = Project2Record.objects.filter(valid_filter_p2)

    total_live = count_live(p1) + count_live(p2)
    total_still = count_still(p1) + count_still(p2)
    total_deliveries = total_live + total_still

    # 🔹 gestational age fields
    ga_fields = [
        "gestation_age",
        "estimated_date_of_delivery",
        "q40_if_available_estimated_ga_through_ultrasound_before_20_weeks_in_weeks",
    ]

    def count_ga_records(qs):
        cond = Q()
        for f in ga_fields:
            if f in [fld.name for fld in qs.model._meta.get_fields()]:
                cond |= (~Q(**{f"{f}__isnull": True}) & ~Q(**{f"{f}__exact": ""}))
        return qs.filter(cond).distinct().count()

    ga_available = count_ga_records(p1) + count_ga_records(p2)
    ga_not_available = total_deliveries - ga_available if total_deliveries else 0

    percent_available = round((ga_available / total_deliveries * 100), 2) if total_deliveries else 0
    percent_missing = 100 - percent_available if total_deliveries else 0

    return JsonResponse(
        {
            "selected_dag": dag if dag else "All",
            "total_deliveries": total_deliveries,
            "gestational_age_available": ga_available,
            "gestational_age_not_available": ga_not_available,
        }
    )


#########GA age category#######


def ga_count_total_deliveriess(request):
    """
    Returns total deliveries (Live + Still/IUD),
    GA available/not available,
    and GA distribution by category (<28, 28–31, 32–33, 34–36, >=37).
    """

    dag = request.GET.get("dag", "").strip()

    # 🔹 check if each model actually has data_access_group
    p1_fields = [f.name for f in Project1Record._meta.get_fields()]
    p2_fields = [f.name for f in Project2Record._meta.get_fields()]

    valid_filter_p1 = Q()
    valid_filter_p2 = Q()

    if "data_access_group" in p1_fields:
        valid_filter_p1 &= ~Q(data_access_group__isnull=True) & ~Q(data_access_group__exact="")
        if dag and dag.lower() != "all":
            valid_filter_p1 &= Q(data_access_group__iexact=dag)

    if "data_access_group" in p2_fields:
        valid_filter_p2 &= ~Q(data_access_group__isnull=True) & ~Q(data_access_group__exact="")
        if dag and dag.lower() != "all":
            valid_filter_p2 &= Q(data_access_group__iexact=dag)

    # 🔹 delivery status logic
    live_statuses = ["Live Born (Well)", "Live Born (Sick)"]
    still_status = "Still Born / IUD"
    status_fields = ["baby1_status", "baby2_status", "baby3_status"]

    def count_live(qs):
        return sum(qs.filter(**{f"{f}__in": live_statuses}).count() for f in status_fields)

    def count_still(qs):
        return sum(qs.filter(**{f"{f}__exact": still_status}).count() for f in status_fields)

    # 🔹 apply filters safely
    p1 = Project1Record.objects.filter(valid_filter_p1)
    p2 = Project2Record.objects.filter(valid_filter_p2)

    total_live = count_live(p1) + count_live(p2)
    total_still = count_still(p1) + count_still(p2)
    total_deliveries = total_live + total_still

    # 🔹 GA fields (any one means available)
    ga_fields = [
        "gestation_age",
        "estimated_date_of_delivery",
        "q40_if_available_estimated_ga_through_ultrasound_before_20_weeks_in_weeks",
    ]

    def count_ga_records(qs):
        cond = Q()
        for f in ga_fields:
            if f in [fld.name for fld in qs.model._meta.get_fields()]:
                cond |= (~Q(**{f"{f}__isnull": True}) & ~Q(**{f"{f}__exact": ""}))
        return qs.filter(cond).distinct()

    ga_qs = list(count_ga_records(p1)) + list(count_ga_records(p2))
    ga_available = len(ga_qs)
    ga_not_available = total_deliveries - ga_available if total_deliveries else 0

    # 🔹 Categorize GA available values
    categories = {"<28": 0, "28-31": 0, "32-33": 0, "34-36": 0, ">=37": 0}

    for record in ga_qs:
        # handle numeric GA values safely
        ga_val = None
        for field in ga_fields:
            val = getattr(record, field, None)
            if val and str(val).strip().replace(".", "", 1).isdigit():
                ga_val = float(val)
                break

        if ga_val is not None:
            if ga_val < 28:
                categories["<28"] += 1
            elif 28 <= ga_val <= 31:
                categories["28-31"] += 1
            elif 32 <= ga_val <= 33:
                categories["32-33"] += 1
            elif 34 <= ga_val <= 36:
                categories["34-36"] += 1
            elif ga_val >= 37:
                categories[">=37"] += 1

    return JsonResponse(
        {
            "selected_dag": dag if dag else "All",
            "total_deliveries": total_deliveries,
            "gestational_age_available": ga_available,
            "gestational_age_not_available": ga_not_available,
            "ga_categories": categories,
        }
    )


###########analytic dash##########
    

def count_place_vs_delivery_combined(request):
    """
    Returns combined (Project1 + Project2) comparison of:
      - Place of Death (only for dead babies)
      - Place of Delivery (only for delivered babies)
    Categorized by:
      'Public health facility', 'Private health facility', 'Home', 'On the way'
    """

    dag = request.GET.get("dag", None)

    # Common DAG exclusion
    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")

    # --- FIELD DEFINITIONS ---
    death_status_fields = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]
    death_place_fields = [
        "d29_baby_death_place_b1_d14_d7",
        "d29_baby_death_place_b2_d14_d7",
        "d29_baby_death_place_b3_d14_d7",
    ]
    delivery_status_fields = ["baby1_status", "baby2_status", "baby3_status"]
    delivery_location_field = "delivery_location"

    live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
    still_status = 'Still Born / IUD'

    valid_places = [
        "Public health facility",
        "Private health facility",
        "Home",
        "On the way",
    ]

    # Common queryset getter
    def get_queryset(model):
        qs = model.objects.exclude(exclude_dag_filter)
        if dag and dag.lower() != "all":
            qs = qs.filter(data_access_group__iexact=dag)
        return qs

    # ---- PLACE OF DEATH COUNT ----
    def count_places(model):
        qs = get_queryset(model)
        total_dead = 0
        available = 0
        breakdown = {place: 0 for place in valid_places}
        breakdown["Other / Missing"] = 0

        for record in qs.values(*death_status_fields, *death_place_fields):
            for i in range(1, 4):
                status = str(record.get(f"d29_baby_current_status_b{i}") or "").strip()
                place = str(record.get(f"d29_baby_death_place_b{i}_d14_d7") or "").strip()

                if "dead" in status.lower():
                    total_dead += 1
                    if place and place.lower() not in ["", "unknown", "nan"]:
                        available += 1
                        if place in breakdown:
                            breakdown[place] += 1
                        else:
                            breakdown["Other / Missing"] += 1
                    else:
                        breakdown["Other / Missing"] += 1
        return total_dead, available, breakdown

    # ---- DELIVERY PLACE COUNT ----
    def count_deliveries(model):
        qs = get_queryset(model)
        available = 0
        total = 0
        breakdown = {place: 0 for place in valid_places}

        for record in qs.values(*delivery_status_fields, delivery_location_field):
            delivery_location = str(record.get(delivery_location_field) or "").strip()
            for i in range(1, 4):
                status = record.get(f"baby{i}_status")
                if status in live_statuses + [still_status]:
                    total += 1
                    if delivery_location:
                        available += 1
                        if delivery_location in breakdown:
                            breakdown[delivery_location] += 1
        return available, total, breakdown

    # ---- PROJECT COMBINATION ----
    p1_total_dead, p1_avail_dead, p1_death_break = count_places(Project1Record)
    p2_total_dead, p2_avail_dead, p2_death_break = count_places(Project2Record)
    p1_avail_del, p1_total_del, p1_del_break = count_deliveries(Project1Record)
    p2_avail_del, p2_total_del, p2_del_break = count_deliveries(Project2Record)

    # Combine both projects
    total_dead = p1_total_dead + p2_total_dead
    avail_dead = p1_avail_dead + p2_avail_dead
    total_deliveries = p1_total_del + p2_total_del
    avail_deliveries = p1_avail_del + p2_avail_del

    death_breakdown = {
        key: p1_death_break.get(key, 0) + p2_death_break.get(key, 0)
        for key in set(p1_death_break) | set(p2_death_break)
    }
    delivery_breakdown = {
        key: p1_del_break.get(key, 0) + p2_del_break.get(key, 0)
        for key in set(p1_del_break) | set(p2_del_break)
    }

    # Percentages
    percent_death_avail = round((avail_dead / total_dead * 100), 2) if total_dead else 0
    percent_del_avail = round((avail_deliveries / total_deliveries * 100), 2) if total_deliveries else 0

    return JsonResponse({
        "selected_dag": dag or "All",
        "place_of_death": {
            "total_dead": total_dead,
            "available": avail_dead,
            "percent_available": percent_death_avail,
            "breakdown": death_breakdown
        },
        "place_of_delivery": {
            "total_deliveries": total_deliveries,
            "available": avail_deliveries,
            "percent_available": percent_del_avail,
            "breakdown": delivery_breakdown
        }
    })


########3gender analytics 



def count_gender_live_vs_dead(request):
    """
    Returns combined (Project1 + Project2) comparison of gender availability
    for:
      - Live births (Live Born Well/Sick)
      - Dead babies (status contains 'Dead')
    Supports ?dag=<dag_name>
    """

    try:
        dag = request.GET.get("dag", None)
        dag_filter = None if not dag or dag.lower() == "all" else dag.strip().lower()

        # ✅ Common field definitions
        live_statuses = ["Live Born (Well)", "Live Born (Sick)"]
        dead_status_fields = [
            "d29_baby_current_status_b1",
            "d29_baby_current_status_b2",
            "d29_baby_current_status_b3",
        ]
        live_status_fields = ["baby1_status", "baby2_status", "baby3_status"]
        gender_fields = ["baby1_sex", "baby2_sex", "baby3_sex"]

        def process_livebirths(model, dag_filter=None):
            qs = model.objects.all()
            if dag_filter:
                qs = qs.filter(data_access_group__iexact=dag_filter)

            total_live = 0
            gender_available = 0
            gender_missing = 0

            breakdown = {
                "Male": 0,
                "Female": 0,
                "Ambiguous": 0,
                "Unknown": 0
            }

            for rec in qs:
                for i in range(3):
                    status = getattr(rec, live_status_fields[i], None)
                    if status in live_statuses:
                        total_live += 1
                        gender = getattr(rec, gender_fields[i], None)
                        if gender and gender.strip():
                            gender_available += 1
                            g = gender.strip().title()
                            if g in breakdown:
                                breakdown[g] += 1
                            else:
                                breakdown["Unknown"] += 1
                        else:
                            gender_missing += 1

            return total_live, gender_available, gender_missing, breakdown

        def process_deaths(model, dag_filter=None):
            q = Q()
            for f in dead_status_fields:
                q |= Q(**{f"{f}__icontains": "Dead"})
            qs = model.objects.filter(q)
            if dag_filter:
                qs = qs.filter(data_access_group__iexact=dag_filter)

            total_dead = 0
            gender_available = 0
            gender_missing = 0

            breakdown = {
                "Male": 0,
                "Female": 0,
                "Ambiguous": 0,
                "Unknown": 0
            }

            for rec in qs:
                for i in range(3):
                    status = getattr(rec, dead_status_fields[i], None)
                    if status and "dead" in status.lower():
                        total_dead += 1
                        gender = getattr(rec, gender_fields[i], None)
                        if gender and gender.strip():
                            gender_available += 1
                            g = gender.strip().title()
                            if g in breakdown:
                                breakdown[g] += 1
                            else:
                                breakdown["Unknown"] += 1
                        else:
                            gender_missing += 1

            return total_dead, gender_available, gender_missing, breakdown

        # ---- Process both projects ----
        # Live births
        p1_live_total, p1_live_avail, p1_live_missing, p1_live_break = process_livebirths(Project1Record, dag_filter)
        p2_live_total, p2_live_avail, p2_live_missing, p2_live_break = process_livebirths(Project2Record, dag_filter)

        # Dead babies
        p1_dead_total, p1_dead_avail, p1_dead_missing, p1_dead_break = process_deaths(Project1Record, dag_filter)
        p2_dead_total, p2_dead_avail, p2_dead_missing, p2_dead_break = process_deaths(Project2Record, dag_filter)

        # ---- Combine both ----
        live_total = p1_live_total + p2_live_total
        live_avail = p1_live_avail + p2_live_avail
        live_missing = p1_live_missing + p2_live_missing

        dead_total = p1_dead_total + p2_dead_total
        dead_avail = p1_dead_avail + p2_dead_avail
        dead_missing = p1_dead_missing + p2_dead_missing

        live_breakdown = {
            key: p1_live_break.get(key, 0) + p2_live_break.get(key, 0)
            for key in set(p1_live_break) | set(p2_live_break)
        }
        dead_breakdown = {
            key: p1_dead_break.get(key, 0) + p2_dead_break.get(key, 0)
            for key in set(p1_dead_break) | set(p2_dead_break)
        }

        # Percentages
        live_pct = round((live_avail / live_total) * 100, 1) if live_total else 0
        dead_pct = round((dead_avail / dead_total) * 100, 1) if dead_total else 0

        # Distinct DAGs
        dags = (
            list(
                Project1Record.objects.exclude(data_access_group__isnull=True)
                .exclude(data_access_group__exact="")
                .values_list("data_access_group", flat=True)
                .distinct()
            )
            + list(
                Project2Record.objects.exclude(data_access_group__isnull=True)
                .exclude(data_access_group__exact="")
                .values_list("data_access_group", flat=True)
                .distinct()
            )
        )
        dags = sorted(set(dags))

        # ---- Final JSON Response ----
        return JsonResponse({
            "selected_dag": dag if dag else "Overall",
            "available_dags": dags,
            "live_births": {
                "total": live_total,
                "available": live_avail,
                "missing": live_missing,
                "percent_available": live_pct,
                "breakdown": live_breakdown
            },
            "dead_babies": {
                "total": dead_total,
                "available": dead_avail,
                "missing": dead_missing,
                "percent_available": dead_pct,
                "breakdown": dead_breakdown
            }
        })

    except Exception:
        print("❌ Error in count_gender_live_vs_dead:", traceback.format_exc())
        return JsonResponse({"error": "Internal Server Error"}, status=500)



############birthweight##########



def count_birthweight_live_vs_dead(request):
    """
    Returns combined (Project1 + Project2) comparison of birthweight categories:
      - All deliveries (Live + Still Born)
      - Dead babies only
    Categories: <1000, 1000–1499, 1500–2499, ≥2500
    Supports ?dag=<dag_name>
    """

    dag = request.GET.get("dag", None)
    exclude_dag_filter = Q(data_access_group__isnull=True) | Q(data_access_group__exact="")

    birthweight_fields = ["baby1_birthweight", "baby2_birthweight", "baby3_birthweight"]
    status_fields_live = ["baby1_status", "baby2_status", "baby3_status"]
    status_fields_dead = [
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
    ]

    live_statuses = ['Live Born (Well)', 'Live Born (Sick)']
    still_status = 'Still Born / IUD'

    # Helper: Apply DAG filter
    def get_queryset(model):
        qs = model.objects.exclude(exclude_dag_filter)
        if dag and dag.lower() != "all":
            qs = qs.filter(data_access_group__iexact=dag)
        return qs

    # 🧮 For All Deliveries (Live + Still)
    def count_all_birthweights(model):
        qs = get_queryset(model)
        total = available = missing = 0
        categories = {"<1000": 0, "1000-1499": 0, "1500-2499": 0, "≥2500": 0}

        for record in qs.values(*status_fields_live, *birthweight_fields):
            for i in range(1, 4):
                status = record.get(f"baby{i}_status")
                bw = record.get(f"baby{i}_birthweight")
                if status in live_statuses + [still_status]:
                    total += 1
                    if bw and str(bw).strip() != "":
                        try:
                            bw_val = float(bw)
                            available += 1
                            if bw_val < 1000:
                                categories["<1000"] += 1
                            elif 1000 <= bw_val < 1500:
                                categories["1000-1499"] += 1
                            elif 1500 <= bw_val < 2500:
                                categories["1500-2499"] += 1
                            else:
                                categories["≥2500"] += 1
                        except ValueError:
                            missing += 1
                    else:
                        missing += 1
        return available, missing, total, categories

    # 🧮 For Dead Babies Only
    def count_dead_birthweights(model):
        qs = get_queryset(model)
        total_dead = 0
        available = 0
        categories = {"<1000": 0, "1000-1499": 0, "1500-2499": 0, "≥2500": 0}

        for record in qs.values(*status_fields_dead, *birthweight_fields):
            for i in range(1, 4):
                status = str(record.get(f"d29_baby_current_status_b{i}") or "").strip()
                bw = record.get(f"baby{i}_birthweight")
                if "dead" in status.lower():
                    total_dead += 1
                    if bw and str(bw).strip() != "":
                        try:
                            bw_val = float(bw)
                            available += 1
                            if bw_val < 1000:
                                categories["<1000"] += 1
                            elif 1000 <= bw_val < 1500:
                                categories["1000-1499"] += 1
                            elif 1500 <= bw_val < 2500:
                                categories["1500-2499"] += 1
                            else:
                                categories["≥2500"] += 1
                        except ValueError:
                            pass
        return total_dead, available, categories

    # 🔹 Combine both projects
    # All births
    p1_avail_all, p1_missing_all, p1_total_all, p1_cats_all = count_all_birthweights(Project1Record)
    p2_avail_all, p2_missing_all, p2_total_all, p2_cats_all = count_all_birthweights(Project2Record)

    # Dead babies
    p1_dead_total, p1_dead_avail, p1_cats_dead = count_dead_birthweights(Project1Record)
    p2_dead_total, p2_dead_avail, p2_cats_dead = count_dead_birthweights(Project2Record)

    # Combine both
    total_available_all = p1_avail_all + p2_avail_all
    total_missing_all = p1_missing_all + p2_missing_all
    total_deliveries_all = p1_total_all + p2_total_all

    total_dead = p1_dead_total + p2_dead_total
    total_dead_available = p1_dead_avail + p2_dead_avail

    combined_all = {
        key: p1_cats_all.get(key, 0) + p2_cats_all.get(key, 0)
        for key in set(p1_cats_all) | set(p2_cats_all)
    }
    combined_dead = {
        key: p1_cats_dead.get(key, 0) + p2_cats_dead.get(key, 0)
        for key in set(p1_cats_dead) | set(p2_cats_dead)
    }

    percent_all_available = round((total_available_all / total_deliveries_all * 100), 2) if total_deliveries_all else 0
    percent_dead_available = round((total_dead_available / total_dead * 100), 2) if total_dead else 0

    return JsonResponse({
        "selected_dag": dag or "All",
        "birthweight_all": {
            "total": total_deliveries_all,
            "available": total_available_all,
            "missing": total_missing_all,
            "percent_available": percent_all_available,
            "categories": combined_all
        },
        "birthweight_dead": {
            "total_dead": total_dead,
            "available_birthweight": total_dead_available,
            "percent_available": percent_dead_available,
            "categories": combined_dead
        }
    })


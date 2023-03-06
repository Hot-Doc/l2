import subprocess

from api.models import Analyzer
from api.models import ManageDoctorProfileAnalyzer

import simplejson as json
from django.http import JsonResponse


def all_analyzers(request):
    analyzers = [{"label": analyzer.title, "pk": analyzer.id} for analyzer in Analyzer.objects.all().exclude(service_name__isnull=True).exclude(port__isnull=True).order_by('title', 'id')]
    return JsonResponse({"data": analyzers})


def restart_analyzer(request):
    request_data = json.loads(request.body)
    can_restart = request.user.is_superuser or request.user.doctorprofile.has_group('Управление аналаизаторами')
    if can_restart:
        name = ManageDoctorProfileAnalyzer.objects.filter(analyzer_id=request_data["pk"], doctor_profile_id=request.user.doctorprofile.pk).first()
        restart_service = subprocess.Popen(["systemctl", "--user", "restart", name.analyzer.service_name])
        restart_service.wait()
        result = get_status_analyzer(request_data["pk"])
        return JsonResponse({"data": result})
    return JsonResponse(0)


def manage_profile_analyzer(request):
    current_user = request.user.doctorprofile.pk
    filter_analyze = [{"label": g.analyzer.title, "pk": g.analyzer_id} for g in ManageDoctorProfileAnalyzer.objects.filter(doctor_profile_id=current_user).order_by('analyzer', 'id')]
    return JsonResponse({"data": filter_analyze})


def status_analyzer(request):
    request_data = json.loads(request.body)
    can_get_status = request.user.is_superuser or request.user.doctorprofile.has_group('Управление аналаизаторами')
    if can_get_status:
        result = get_status_analyzer(request_data["pk"])
        return JsonResponse({"data": result})
    return JsonResponse(0)


def status_systemctl(request):
    request_data = json.loads(request.body)
    can_get_status = request.user.is_superuser or request.user.doctorprofile.has_group('Управление аналаизаторами')
    if can_get_status:
        result = get_status_systemctl(request_data["pk"])
        return JsonResponse({"data": result})
    return JsonResponse(0)


def get_status_analyzer(pk):
    port = Analyzer.objects.values_list('port', flat=True).get(id=pk)
    lsof_command = ['lsof', '-i', f':{port}']
    process = subprocess.Popen(lsof_command, stdout=subprocess.PIPE)
    output, error = process.communicate()
    res = output.decode().replace(' ', ',')
    res = res.split('\n')
    result = []
    step = 0
    for i in res:
        tmp_res = i.split(',')
        tmp_res = [x for x in tmp_res if x]
        if len(tmp_res) != 0:
            if step != 0:
                a = [tmp_res[1], tmp_res[-1], tmp_res[-2]]
                result.append(a)
            step += 1
    result = [{"pk": pk, "status": i} for i in result]
    return result


def get_status_systemctl(pk):
    service_name = Analyzer.objects.values_list('service_name', flat=True).get(id=pk)
    systemd_command = ['systemctl', '--user', 'status', f'{service_name}']
    proc = subprocess.Popen(systemd_command, stdout=subprocess.PIPE)
    output, error = proc.communicate()
    result = output.decode()
    result = result.split('\n')
    result = [{"pk": pk, "status": i} for i in result]
    return result

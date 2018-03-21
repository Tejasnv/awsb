from django.shortcuts import render
from django.http import HttpResponse
import json
# mongodb
from pymongo import MongoClient
from django.core.paginator import Paginator


# Mongo Connections
client = MongoClient()
db = client.aws
collection = db.dillData
#collection = db.billCollections

listofAcc = []
data = {}
addAccount={}
for account in (collection.find()):
    data[account['accountName']] = account
    data[account['accountName']].pop('_id', None)
#    addAccount.add(account['accountName'])
    listofAcc.append(account['accountName'])
#
#listofAcc = ["binita", "gagan","rahul","binita_2"]
#listofAcc = ["abhijith", "rahul-hourly","rahul"]
selectedAcc = listofAcc
dateRange=["none"]

def gatherData(selectedAcc):
    service = {}
    for i in selectedAcc:
        for j in data[i].keys():
            if type(data[i][j]) is dict:
                for k in data[i][j].keys():
                    if (service.get(j)):
                        service[j] = service[j] + "," + k
                    else:
                        service[j] = k
            else:
                pass

    for j in service.keys():
        l = list(set(service[j].split(",")))
        service[j] = {'products': l}

    for i in selectedAcc:
        for j in data[i].keys():
            if type(data[i][j]) is dict:
                sum = 0.0
                for k in data[i][j].keys():
                    for l in range(len(data[i][j][k])):
                        if(dateRange[0] != "none"):
                            currDate = data[i][j][k][l][4][:len(dateRange[0])+2].replace("-", "")
                            if(currDate in dateRange ):                    
                                sum = sum + float(data[i][j][k][l][3])
                        if(dateRange[0] == "none"):
                            sum = sum + float(data[i][j][k][l][3])
                if(service[j].get('price')):
                    service[j]['price'] = service[j]['price'] + sum
                else:
                    service[j]['price'] = sum

    for services in service:
            for acc in selectedAcc:
                if ((data[acc].get(services))):
                    for products in service[services]['products']:
                        if(data[acc][services].get(products)):
                            for val in range(0,len(data[acc][services][products])):
                                currDate = data[acc][services][products][val][4][:len(dateRange[0])+2]
                                if(dateRange[0] == "none"):
                                    if(data[acc][services][products][val][2] == ""):
                                        res = data[acc][services][products][val][4],data[acc][services][products][val][1],data[acc][services][products][val][2],data[acc][services][products][val][3]
                                    else:
                                        res = data[acc][services][products][val][4],data[acc][services][products][val][1],data[acc][services][products][val][2],data[acc][services][products][val][3]
                                    if(service[services].get(products)):
                                        service[services][products].append(res)
                                    else:
                                        service[services][products] = [res]
                                elif(len(dateRange) == 1):
                                    if(int(currDate.replace("-", "")) == int(dateRange[0])):
                                        if(data[acc][services][products][val][2] == ""):
                                            res = data[acc][services][products][val][4],data[acc][services][products][val][1],data[acc][services][products][val][2],data[acc][services][products][val][3]
                                        else:
                                            res = data[acc][services][products][val][4],data[acc][services][products][val][1],data[acc][services][products][val][2],data[acc][services][products][val][3]
                                        if(service[services].get(products)):
                                            service[services][products].append(res)
                                        else:
                                            service[services][products] = [res]
 
                                elif(len(dateRange) == 7):
                                    if((currDate.replace("-", "")) in (dateRange)):
                                        if(data[acc][services][products][val][2] == ""):
                                            res = data[acc][services][products][val][4],data[acc][services][products][val][1],data[acc][services][products][val][2],data[acc][services][products][val][3]
                                        else:
                                            res = data[acc][services][products][val][4],data[acc][services][products][val][1],data[acc][services][products][val][2],data[acc][services][products][val][3]
                                        if(service[services].get(products)):
                                            service[services][products].append(res)
                                        else:
                                            service[services][products] = [res]
                        else:
                            pass
                else:
                    pass

#Trim data
    for i in service.keys():
        for k in service[i]['products']:
            if k not in service[i].keys():
                service[i]['products'].remove(k)

    for i in service.keys():
        for k in service[i]['products']:
            if k not in service[i].keys():
                service[i]['products'].remove(k)

    for i in service.keys():
        for k in service[i]['products']:
            if k not in service[i].keys():
                service[i]['products'].remove(k)

    return (service)

#print (service['AWSGlue'])

def daily(request):
    global dateRange 
    dateRange = ["none"]
    service = gatherData(selectedAcc)
    return render(request, 'bill/daily.html', {'dictionary': service, 'accounts':listofAcc })

def weekly(request):    
    service = gatherData(selectedAcc)
    return render(request, 'bill/weekly.html', {'dictionary': service, 'accounts':listofAcc })

def monthly(request):
    service = gatherData(selectedAcc)
    return render(request, 'bill/monthly.html', {'dictionary': service, 'accounts':listofAcc })

def index(request):
    global dateRange 
    dateRange = ["none"]
    service = gatherData(selectedAcc)
    return render(request, 'bill/index.html', {'dictionary': service, 'accounts':listofAcc })

def getday(request):
    if request.method == 'GET':
        global selectedAcc
        global dateRange
### Select Services 
        if (request.GET['action'] == 'selection'):
            selectService = request.GET.getlist('select[]')

            service = gatherData(selectedAcc)
            result = {}
            
            if(selectService[0] == "none"):
                result = service
            else:    
                for i in selectService:
                    result[i] = service[i]

            return render(request, 'bill/populate.html', {'dictionary': result})

### User update
        if (request.GET['action'] == 'userupdate'):
            user = request.GET['user']

            if(user == "none"):
                selectedAcc = listofAcc 
            else:   
                selectedAcc = [user]
            service = gatherData(selectedAcc)
            result = {}
            
            return render(request, 'bill/populate.html', {'dictionary': service})

### Daily Date updates
        if (request.GET['action'] == 'daily'):
            selectedDate = request.GET['value']

            dateRange = [selectedDate]
            service = gatherData(selectedAcc)
            
            return render(request, 'bill/populate.html', {'dictionary': service})

### Weekley Date updates
        if (request.GET['action'] == 'weekly'):
            datesOfWeek = request.GET.getlist('value[]')

            dateRange = datesOfWeek
            service = gatherData(selectedAcc)

            daysDistribution = {}

            for key,val in service.items():
                daysDistribution[key] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0]
                for k,v in val.items():
                    sum = 0.0
                    if ((k != 'products') and (k != 'price')):
                        for i in v:
                            currDate = i[0][0:10].replace("-", "")
                            indexVal = dateRange.index(currDate)
                            daysDistribution[key][indexVal] = float(daysDistribution[key][indexVal]) + float(i[3])

            return render(request, 'bill/populate.html', {'dictionary': service, 'daysDistri':daysDistribution})

### Monthly Date updates
        if (request.GET['action'] == 'monthly'):
            getValues = request.GET.getlist('values[]')

            yearMonth = getValues[0]
            dateRange = [yearMonth]
            service = gatherData(selectedAcc)

            daysDistribution = {}

            for key,val in service.items():
                daysDistribution[key] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                for k,v in val.items():
                    sum = 0.0
                    if ((k != 'products') and (k != 'price')):
                        for i in v: 
                            currDate = i[0][0:10].replace("-", "")
                            justDay = i[0][8:10]

                            if ((int(justDay) + int(getValues[2]) - 1) < 7):
                                daysDistribution[key][0] = float(daysDistribution[key][0]) + float(i[3])
                            elif ((int(justDay) + int(getValues[2]) - 1) < 14):
                                daysDistribution[key][1] = float(daysDistribution[key][1]) + float(i[3])
                            elif ((int(justDay) + int(getValues[2]) - 1) < 21):
                                daysDistribution[key][2] = float(daysDistribution[key][2]) + float(i[3])
                            elif ((int(justDay) + int(getValues[2]) - 1) < 28):
                                daysDistribution[key][3] = float(daysDistribution[key][3]) + float(i[3])
                            elif ((int(justDay) + int(getValues[2]) - 1) < 35):
                                daysDistribution[key][4] = float(daysDistribution[key][4]) + float(i[3])

            return render(request, 'bill/populate.html', {'dictionary': service, 'daysDistri':daysDistribution})

def update(request):
    if request.method == 'GET':
        if (request.GET['action'] == 'show'):
#            selectedDate = request.GET.getlist['startdate[]']
#            getValues = request.GET.getlist('values[]')
            get = request.GET['value']
            servProd =  get.split(" ")

#            dateRange = [selectedDate]
            service = gatherData(selectedAcc)

            cursor = {}

            for key,val in service.items():
                if (key == servProd[0]):
                    for k,v in val.items():
                        if( k == servProd[1]):
                            for i in v:
                                if(cursor.get(k)):
                                    cursor[k].append(i)
                                else:
                                    cursor[k] = [i]

            return render(request, 'bill/products.html', {'curs': cursor})
            return HttpResponse('a')

        else:
            return HttpResponse('')

#        for key,val in service.items():
#            for k,v in val.items():
#                if ((k != 'products') and (k != 'price')):
#                    for i in v: 
#                        cursor[i] = v


#        for key,value in service.items():
#            cursor[l] = [data[i][j][k][l][59], data[i][j][k][l][38],data[i][j][k][l][1], data[i][j][k][l][22]]            


'''
    if request.method == 'GET':
        if (request.GET['action'] == 'shows'):

            get = request.GET['value']
            get = get.split(" ")
            cursor = {}

            if (request.GET.getlist('startdate[]')):
                startdate = request.GET.getlist('startdate[]')
            else:
                startdate = request.GET['startdate']

            splitIndexBy = 10
            daysdistribution = {}

            for i in data.keys():
                for j in data[i].keys():
                    if (j == get[0]):
                        for k in data[i][j].keys():
                            if (k == get[1]):
                                for l in range(len(data[i][j][k])):
                                    if (startdate == 'null'):
                                        cursor[l] = [data[i][j][k][l][59], data[i][j][k][l][38], data[i][j][k][l][1],
                                                     data[i][j][k][l][22]]
                                    else:
                                        currDate = (data[i][j][k][l][1])[:splitIndexBy]
                                        currDate = currDate.replace("-", "")
                                        if (type(startdate) == list):
                                            for x in range(len(startdate)):
                                                q = str(l) + str(x)
                                                if (daysdistribution.get(startdate[x])):
                                                    pass
                                                else:
                                                    daysdistribution[startdate[x]] = 00.00

                                                if (int(startdate[x]) == int(currDate)):
                                                    cursor[q] = [data[i][j][k][l][59], data[i][j][k][l][38],
                                                                 data[i][j][k][l][1], data[i][j][k][l][22]]
                                                    if (daysdistribution.get(startdate[x])):
                                                        daysdistribution[startdate[x]] = float(
                                                            daysdistribution[startdate[x]]) + float(
                                                            data[i][j][k][l][22])
                                                    else:
                                                        daysdistribution[startdate[x]] = float(data[i][j][k][l][22])
                                        else:
                                            if (len(startdate) == 8):
                                                if (int(startdate) == int(currDate)):
                                                    cursor[l] = [data[i][j][k][l][59], data[i][j][k][l][38],
                                                                 data[i][j][k][l][1], data[i][j][k][l][22]]
                                            elif (len(startdate) == 6):
                                                currDate = (data[i][j][k][l][1])[:7]
                                                currDate = currDate.replace("-", "")
                                                if (int(startdate) == int(currDate)):
                                                    cursor[l] = [data[i][j][k][l][59], data[i][j][k][l][38],
                                                                 data[i][j][k][l][1], data[i][j][k][l][22]]

            return render(request, 'bill/products.html', {'curs': cursor, 'daysDistribution': daysdistribution})
        else:
            return HttpResponse('')
'''
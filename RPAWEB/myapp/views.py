from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from utils.OracleConnect import get_db_connection
from .forms import LoginForm
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView
from .models import Order
from django.db.models import Q
import logging
from datetime import datetime

connection = get_db_connection()
   
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
    
class MyLoginView(LoginView):
    template_name = 'login.html'

def fetchCustomer(request):
    # Custom query to fetch data
    with connection.cursor() as cursor:
       cursor.execute("select description from MST_CUSTOMER_B2B_WA where report_flow=1 order by description")
       rows = cursor.fetchall()  # Fetches data as a list of tuples
       
       # Preparing data for rendering
    datacus = [{'description': row[0], } for row in rows]
    
    # Passing data to the template
    return render(request, 'data_table.html', {'data': datacus})    
  
def load_data_view_ori(request):
    # Custom query to fetch data
    with connection.cursor() as cursor:
       #cursor.execute("SELECT id, name, age FROM your_table")
       cursor.execute("select username,fullname,OTORISASI from MST_USER")
       rows = cursor.fetchall()  # Fetches data as a list of tuples
    # Preparing data for rendering
    data = [{'username': row[0], 'fullname': row[1], 'OTORISASI': row[2]} for row in rows]
    
    # Passing data to the template
    return render(request, 'data_table.html', {'data': data})    

def load_data_view(request):
    search_term = request.GET.get('search_term', '')
    # Custom query to fetch data
    with connection.cursor() as cursor:
       #cursor.execute("SELECT id, name, age FROM your_table")
       query="select username,fullname,OTORISASI from MST_USER where 1=1 and upper(fullname) like :search_term"
       cursor.execute(query,{'search_term': f'%{search_term}%'})
       rows = cursor.fetchall()  # Fetches data as a list of tuples
    # Preparing data for rendering
    data = [{'username': row[0], 'fullname': row[1], 'OTORISASI': row[2]} for row in rows]
    with connection.cursor() as cursor:
       #cursor.execute("SELECT id, name, age FROM your_table")
       cursor.execute("select description from MST_CUSTOMER_B2B_WA where report_flow=1 order by description")
       rows = cursor.fetchall()  # Fetches data as a list of tuples
    # Preparing data for rendering
    datacus = [{'description': row[0],} for row in rows]
    
    # Passing data to the template
    return render(request, 'data_table.html', {'data': data,'datacus':datacus})    

def oracle_data_view(request):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT 'connected' FROM mst_gcm where condition='COUNT_FOLDER'")
        rows = cursor.fetchall()
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        return HttpResponse(f"Connection successful! Result: {rows}")
    else:
        return HttpResponse("Failed to connect to Oracle")
    
def is_user_authenticated(request):
    return request.session.get('is_authenticated', False)    
    
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Database connection and query
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute("""
                        SELECT username, password, fullname, otorisasi 
                        FROM MST_USER 
                        WHERE username = :username AND password = :password
                    """, {'username': username, 'password': password})
                    
                    result = cursor.fetchone()
                    
                    if result:
                        # Create session data dictionary
                        user_data = {
                            'username': result[0],
                            'fullname': result[2],
                            'otorisasi': result[3],
                            'is_authenticated': True,
                            'login_time': timezone.now().isoformat()
                        }
                        
                        # Set all session data
                        for key, value in user_data.items():
                            request.session[key] = value

                        # Calculate midnight expiry
                        now = timezone.now()
                        midnight = (now + datetime.timedelta(days=1)).replace(
                            hour=0, minute=0, second=0, microsecond=0
                        )
                        seconds_until_midnight = int((midnight - now).total_seconds())
                        
                        # Set session expiry
                        request.session.set_expiry(seconds_until_midnight)
                        
                        # Log successful login
                        logger = logging.getLogger('django')
                        logger.info(f"User {result[2]} logged in successfully")

                        return redirect('home')
                    else:
                        return render(request, 'login.html', {
                            'form': form, 
                            'login_failed': True
                        })
                        
                except Exception as e:
                    logger = logging.getLogger('django')
                    logger.error(f"Login error: {str(e)}")
                    messages.error(request, "An error occurred during login")
                    
                finally:
                    cursor.close()
                    connection.close()
            else:
                messages.error(request, "Database connection failed")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
# myapp/views.py

# Logout view
def logout_view(request):
    # Clear all session data
    request.session.flush()
    return redirect('login')

class OrderListView(ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        queryset = Order.objects.all()
        customer = self.request.GET.get('customer')
        date = self.request.GET.get('date')
        dist_channel = self.request.GET.get('dist_channel')
        
        if customer and customer != 'ALL':
            queryset = queryset.filter(customer=customer)
        if date:
            queryset = queryset.filter(file_date__date=date)
        if dist_channel and dist_channel != 'ALL':
            queryset = queryset.filter(dist_channel=dist_channel)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source_count'] = self.get_queryset().count()
        context['download_count'] = self.get_queryset().exclude(
            Q(so_number='') | Q(so_number__isnull=True)
        ).count()
        context['ocr_count'] = self.get_queryset().exclude(
            Q(po_number='') | Q(po_number__isnull=True)
        ).count()
        return context


def FlowPOSO(request):
    search_term = request.GET.get('search_term', '')
    selected_customer = request.GET.get('cmb_Customer', '')  # Get selected customer from request
    selected_date = request.GET.get('date', '')  # Capture the date
    selected_dist_channel = request.GET.get('cmb_DistChannel', '')  # Get selected customer from request
    rowsPerPage = request.GET.get('cmb_rowsPerPage', '')  # Get selected row per page from request
    pages = request.GET.get('ActivePages', '')  # Get selected customer from request
    # Capture checkboxes (value="on" when checked, None when unchecked)
    belum_download = request.GET.get('belum_download', '') == 'on'
    belum_so = request.GET.get('belum_so', '') == 'on'
    belum_ocr = request.GET.get('belum_ocr', '') == 'on'
    belum_po = request.GET.get('belum_po', '') == 'on'
    kolom_download = request.GET.get('kolom_download', '') == 'on'
    kolom_ocr   = request.GET.get('kolom_ocr', '') == 'on'
    
    if rowsPerPage is None or rowsPerPage == '':
        rowsPerPage=10
    if pages is None or pages == '':
        pages=1
        
    formatted_date = ''
    if selected_date is None or selected_date == '':
        formatted_date = datetime.now().strftime("%d %b %Y").upper()
        selected_date = datetime.now().strftime("%Y-%m-%d")
    else:    
        formatted_date = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%d %b %Y").upper()

    
    datacus=ComboBoxCustomer()
    datadischan=ComboBoxDistChan()
    DataTablePOSO=TablePOSO(search_term,selected_customer,formatted_date,selected_dist_channel,
                            belum_download,belum_so,belum_ocr,belum_po,rowsPerPage,pages)   
    DataTablePOSOCount=TablePOSOCount(search_term,selected_customer,formatted_date,selected_dist_channel,
                            belum_download,belum_so,belum_ocr,belum_po)   
    
    print("======Debugging=====")
    print(f"Search Term: {search_term}")  # Debugging
    print(f"Selected Customer: {selected_customer}")  # Debugging
    print(f"Selected Date: {selected_date}")  # Debugging
    print(f"Formatted Date: {formatted_date}")  # Debugging
    print(f"Selected Dist Channel: {selected_dist_channel}")  # Debugging
    print(f"DataTablePOSOCount :{DataTablePOSOCount}") #debugging
    print(f"Belum Download: {belum_download}")  # Debugging
    print(f"Belum SO: {belum_so}")  # Debugging 
    print(f"Belum OCR: {belum_ocr}")  # Debugging
    print(f"Belum PO: {belum_po}")  # Debugging
    print(f"Kolom Download: {rowsPerPage}")  # Debugging
    print(f"rowPerPages : {rowsPerPage}")  # Debugging
    print(f"Pages : {pages}")  # Debugging
    
    return render(request, 'FlowPOSO.html', {
        'data': datacus,
        'dischan': datadischan,
        'TablePOSO': DataTablePOSO,
        'TablePOSOCount': DataTablePOSOCount,
        'search_term': search_term,
        'selected_date': selected_date,
        'selected_dist_channel': selected_dist_channel,
        'selected_customer': selected_customer  ,
        'belum_download': belum_download,
        'belum_so': belum_so,
        'belum_ocr': belum_ocr,
        'belum_po': belum_po,
        'kolom_download': kolom_download,
        'kolom_ocr': kolom_ocr,
        'rowsPerPage': rowsPerPage,
        'pages': pages
    })

    # search_term = request.GET.get('search_term', '')
    # with connection.cursor() as cursor:
    #    #cursor.execute("SELECT id, name, age FROM your_table")
    #    query="select username,fullname,OTORISASI from MST_USER where 1=1 and upper(fullname) like :search_term"
    #    cursor.execute(query,{'search_term': f'%{search_term}%'})
    #    rows = cursor.fetchall()  # Fetches data as a list of tuples
    # # Preparing data for rendering
    
def ComboBoxCustomer():
    with connection.cursor() as cursor:
       cursor.execute("select description from MST_CUSTOMER_B2B_WA where report_flow=1 order by description")
       rows = cursor.fetchall()  # Fetches data as a list of tuples
    return [{'description': row[0]} for row in rows]  

def ComboBoxDistChan():
    with connection.cursor() as cursor:
       cursor.execute("select gcm_id dischan,gcm_id||'-'||description detail from MST_GCM where condition='DIST_CHANNEL' ORDER BY gcm_id")
       rows = cursor.fetchall()  # Fetches data as a list of tuples
    return [{'dischan': row[0],'detail': row[1]} for row in rows] 

def TablePOSO(vSearch,vCustomer,vSelectedDate,vSelectedDistChannel,
              vBelumDownload,vBelumSO,vBelumOCR,vBelumPO,vRowsPerPage,vPages):
    with connection.cursor() as cursor:
        
        where_clause = "1=1"
        params = {'search_term': f'%{vSearch}%'}
        
        # Add customer filter if a specific customer is selected
        if vCustomer and vCustomer != "ALL":
            where_clause += " AND CUSTOMER = :customer"
            params['customer'] = vCustomer
            
        if vSelectedDistChannel and vSelectedDistChannel != "ALL":
            where_clause += " AND DISTRIBUTION_CHANNEL = :distchannel"
            params['distchannel'] = vSelectedDistChannel    
        
        if  vBelumDownload :
            where_clause += " AND FILENAME_DOWNLOAD IS NULL"
       
        if vBelumSO :
            where_clause += " AND SO_NUMBER IS NULL"
            
        if vBelumOCR :
            where_clause += " AND FILENAME_OCR IS NULL"    
            
        if vBelumPO :
            where_clause += " AND PO_XPI IS NULL"    
        
 
        
        where_clause += " AND trunc(DATE_ASOF) = :dateasof"    
        params['dateasof'] = vSelectedDate
            
        where_clause +="""
        AND (FILENAME_SOURCE LIKE :search_term OR 
                 FILENAME_DOWNLOAD LIKE :search_term OR
                 PO_XPI LIKE :search_term OR SO_NUMBER LIKE :search_term OR 
                 KODE_VENDOR LIKE :search_term OR NOTES LIKE :search_term)
        """    
        
        print(type(vPages))
        print(type(vRowsPerPage))
         # Build the WHERE condition dynamically
        if vRowsPerPage is None or vRowsPerPage == "":
            vRowsPerPage=10
         
        if vPages is None or vPages == '':
            vPages=1       
            
        vOffset = (int(vPages) - 1) * int(vRowsPerPage)
        where_clause += f" OFFSET {vOffset} ROWS FETCH NEXT {vRowsPerPage} ROWS ONLY"
        #print(where_clause)
        vQuery = f"""
            SELECT 
                DATE_GENERATE,
                TIME_GENERATE,
                TO_CHAR(DATE_ASOF, 'DD/MM/YYYY HH24:MI:SS') AS DATE_ASOF,
                CUSTOMER,
                FILE_SOURCE,
                FILENAME_SOURCE,
                TO_CHAR(FILENAME_SOURCE_DATE, 'DD/MM/YYYY HH24:MI:SS') AS FILENAME_SOURCE_DATE,
                FILENAME_DOWNLOAD,
                TO_CHAR(FILENAME_DOWNLOAD_DATE, 'DD/MM/YYYY HH24:MI:SS') AS FILENAME_DOWNLOAD_DATE,
                FILENAME_OCR,
                TO_CHAR(FILENAME_OCR_DATE, 'DD/MM/YYYY HH24:MI:SS') AS FILENAME_OCR_DATE,
                PO_XPI,
                TO_CHAR(PO_XPI_DATE, 'DD/MM/YYYY HH24:MI:SS') AS PO_XPI_DATE,
                SO_NUMBER,
                TO_CHAR(SO_DATE, 'DD/MM/YYYY HH24:MI:SS') AS SO_DATE,
                NOTES,
                DISTRIBUTION_CHANNEL,
                RETURN_SAP,
                INFO_JADWALTOKO,
                TO_NUMBER(TRIM(TOTAL_PRICE)) AS TOTAL_PRICE,
                KODE_VENDOR,
                ROWNUM               
            FROM B2BROBOTIK.TRX_DASHBOARD_FLOW_PO 
            WHERE {where_clause}
        """
        #print(vQuery)  # Debugging
        cursor.execute(vQuery,params)
        rows = cursor.fetchall()  # Fetches data as a list of tuples

    # Transform fetched rows into a list of dictionaries
    return [
        {
            'DATE_GENERATE': row[0],
            'TIME_GENERATE': row[1],
            'DATE_ASOF': row[2],
            'CUSTOMER': row[3],
            'FILE_SOURCE': row[4],
            'FILENAME_SOURCE': row[5],
            'FILENAME_SOURCE_DATE': row[6],
            'FILENAME_DOWNLOAD': row[7],
            'FILENAME_DOWNLOAD_DATE': row[8],
            'FILENAME_OCR': row[9],
            'FILENAME_OCR_DATE': row[10],
            'PO_XPI': row[11],
            'PO_XPI_DATE': row[12],
            'SO_NUMBER': row[13],
            'SO_DATE': row[14],
            'NOTES': row[15],
            'DISTRIBUTION_CHANNEL': row[16],
            'RETURN_SAP': row[17],
            'INFO_JADWALTOKO': row[18],
            'TOTAL_PRICE': row[19],
            'KODE_VENDOR': row[20],
            'ROWNUM': row[21],            
        }
        for row in rows
    ]

    

def TablePOSOCount(vSearch,vCustomer,vSelectedDate,vSelectedDistChannel,
              vBelumDownload,vBelumSO,vBelumOCR,vBelumPO):
    with connection.cursor() as cursor:
        
         # Build the WHERE condition dynamically
        where_clause = "1=1"
        params = {'search_term': f'%{vSearch}%'}

        # Add customer filter if a specific customer is selected
        if vCustomer and vCustomer != "ALL":
            where_clause += " AND CUSTOMER = :customer"
            params['customer'] = vCustomer
            
        if vSelectedDistChannel and vSelectedDistChannel != "ALL":
            where_clause += " AND DISTRIBUTION_CHANNEL = :distchannel"
            params['distchannel'] = vSelectedDistChannel    
        
        if  vBelumDownload :
            where_clause += " AND FILENAME_DOWNLOAD IS NULL"
       
        if vBelumSO :
            where_clause += " AND SO_NUMBER IS NULL"
            
        if vBelumOCR :
            where_clause += " AND FILENAME_OCR IS NULL"    
            
        if vBelumPO :
            where_clause += " AND PO_XPI IS NULL"    
        
        where_clause += " AND trunc(DATE_ASOF) = :dateasof"    
        params['dateasof'] = vSelectedDate
            
            
        where_clause +="""
        AND (FILENAME_SOURCE LIKE :search_term OR 
                 FILENAME_DOWNLOAD LIKE :search_term OR
                 PO_XPI LIKE :search_term OR SO_NUMBER LIKE :search_term OR 
                 KODE_VENDOR LIKE :search_term OR NOTES LIKE :search_term)
        """    
        vQuery = f"""
           SELECT COUNT (FILENAME_SOURCE) SOURCE,
		   COUNT (FILENAME_DOWNLOAD) DOWNLOAD,
		   COUNT (FILENAME_OCR) OCR,
		   COUNT (PO_XPI) PO,
		   COUNT (SO_NUMBER) SO
  FROM B2BROBOTIK.TRX_DASHBOARD_FLOW_PO
            WHERE {where_clause}
        """
        #print(vQuery)  # Debugging
        cursor.execute(vQuery,params)
        rows = cursor.fetchall()  # Fetches data as a list of tuples

    # Transform fetched rows into a list of dictionaries
    data_list = [
        {
        'SOURCE': row[0],
        'DOWNLOAD': row[1],
        'OCR': row[2],
        'PO': row[3],
        'SO': row[4]
    }
    for row in rows
    ]

        # Pass only the first dictionary if available
    context = {'CountData': data_list[0] if data_list else None}

    # return context
    return data_list[0]
from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
import requests
from PIL import Image
import bs4
import os
import re
from datetime import datetime
import matplotlib.pyplot as plt
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from Website.utils import render_to_pdf

#from django.http import HttpResponseRedirect
#from django.core.urlresolvers import reverse


# Create your views here.


@login_required
def Home(request):
    td = datetime.now()
    osName = ''
    if os.name =='nt':
            osName =osName.replace('','windows')
    else:
        pass
    context = {'today':td,'os_name':osName,'name':request.user.username}
    return render(request,'mainpage/home.html',context)
   
@login_required
def About(request):
    name = ' Shop adviser'
    version = ' Version V1.01'
    developer = ' Ezra Chirchir'
    contact = '@ezrachirii'
    email = 'kipkiruichirii@outlook.com'
    license_ = 'It\'s under the common BSD licence.All code can be downloaded on GitHub Repository'
    Thanks = 'Let me pass my Sincere gratitude to the University Supervisor Madam Lily Siele, and all the lecturers at the University of Eldoret.'
    
    
    context = {'name':name,'version':version,'developer':developer,'contact':contact,'email':email,'license':license_,'Thanks':Thanks}
    return render(request,'mainpage/about.html',context)
@login_required
def analytics(request):
    query = request.GET.get('q')
    price = []
    if query == None:
        query = 'samsung galaxy s7'
    else:
        query = query
    query_modified = query.replace(' ', '+')
    #defining the function that would scrape the various websites 
 
    def avechiScrapper(productUrl):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        }
        res = requests.get(productUrl, headers=headers)
        res.raise_for_status()


        soup = bs4.BeautifulSoup(res.text, 'lxml')
        #elms = soup.select('.woocommerce-Price-amount amount')
        ins = soup.find_all('span',{'class':'price'})
        if ins==[]:
            #print("Product not found")
            price_none = 0
            price.insert(0,price_none)
        else:
            price_ins= ins[0].span.replace_with('').text
            priceAvechi = float(price_ins[4:].replace(',',''))/98
            price.insert(0,priceAvechi)
   


    def killmallScraper(productUrl):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        }
        res = requests.get(productUrl, headers=headers)
        res.raise_for_status()


        soup = bs4.BeautifulSoup(res.text, 'lxml')
        elms = soup.select('.sale-price')
        price_ = elms[0].string
        price_ = price_[4:]
        price_ = price_.replace(',','')
        price_= float(price_)
        killMallprice=price_
        price.insert(1,killMallprice/98)
       
        

    def JumiaScraper(productUrl):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        }
        res = requests.get(productUrl, headers=headers)
        res.raise_for_status()


        soup = bs4.BeautifulSoup(res.text, 'lxml')
        #elms = soup.select('.price')
        price_container =  soup.find_all('span', attrs={'dir':'ltr','data-price':re.compile('\d+')})
        price_jumia = price_container[0].get_text('data-price')
        price_jumia= price_jumia.replace(',','')
        price_jumia = int(price_jumia)/98
        price_raw =str(price_jumia)
        new_price = float(price_raw[:6])-48.76
        jumiaPrice = new_price
        if jumiaPrice <0:
            jumiaPrice = str(jumiaPrice)[1:]
            jumiaPrice = float(jumiaPrice)
        else:
            jumiaPrice=float(new_price)
        price.insert(2,jumiaPrice)
           
    """"def ebayScraper(productUrl):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        }
        res = requests.get(productUrl, headers=headers)
        res.raise_for_status()


        soup = bs4.BeautifulSoup(res.text, 'lxml')
        elms = soup.select('.bold')
        price_elms = []
        for el in elms:
            if(el.string != None):
                price_elms.append(el.string.strip())
            else:
                pass
        #print(price_elms)
        priceEbay1 = price_elms[0]
        priceEbay2 = price_elms[1]
        priceEbay3 = price_elms[2]
        priceEbay1=priceEbay1[1:]
        priceEbay2=priceEbay2[1:]
        priceEbay3=priceEbay3[1:]
        priceEbayList = [priceEbay1,priceEbay2,priceEbay3]
        priceEbay= max(priceEbayList)
        priceEbay = float(priceEbay)
        price.insert(3,priceEbay)"""
        
   

    avechiScrapper('https://www.avechi.com/?product_cat=&post_type=product&s='+query_modified)
    killmallScraper('https://www.kilimall.co.ke/?act=search&keyword='+query_modified)
    JumiaScraper('https://www.jumia.co.ke/catalog/?q='+query_modified)
   # ebayScraper('https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2050601.m570.l1313.TR0.TRC0.H0.X'+query_modified +'TRS0&_nkw='+query_modified+'&_sacat=0')
    
  
    #the contexts
    def generate_pdf(request,*args,**kwargs):
        template = get_template('mainpage/analytics.html')
        context = {
            "avechi":price[0],
            "killmall":price[1],
            "jumia":price[2],
            
        }
        pdf = render_to_pdf('mainpage/analytics.html',context)
        if pdf:
             response = HttpResponse(pdf,content_type ='application/pdf')
             filename = "invoice_%d.pdf" %({{query_modified.replace("+"," ")}})
             content = "inline;filename='%s'" %(filename)
             response ['Content-Disposition']=content
             return response
        else:
            return HttpResponse("Not Found")
    def deleteimage():
         try:
            im = Image.open('/static/'+query_modified+'.png')
            if im:
                os.remove(im)
            else:
                pass
         except:
            pass
    deleteimage()
         


    def plots():
        labels = 'Avechi.com', 'Killmall.co.ke', 'Jumia.co.ke'
        sizes = [x for x in price]
        if len(sizes)<len(labels):
            sizes.append(0)
        colors = ['gold', 'yellowgreen', 'lightcoral', ]
        explode = (0.1, 0,0)  # explode 1st slice
         
        # Plot
        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
         
        plt.axis('equal')
        plt.savefig('ezraWeb/static/'+query_modified+'.png')
    plots()
    shops = ['Killmall.co.ke','Avechi.com','Jumia.co.ke']
   
    context = {'query':query,'price':price,'shops':shops,'query_modified':query_modified}
    return render(request,'mainpage/analytics.html',context)
    
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
@login_required
def generate_pdf(request,*args,**kwargs):
        template = get_template('mainpage/analytics.html')
        context = {
            "avechi":price[0],
            "killmall":price[1],
            "jumia":price[2],
            
        }
        html = template.render(context)
        pdf = render_to_pdf('mainpage/analytics.html',context)
        if pdf:
             response = HttpResponse(pdf,content_type ='application/pdf')
             filename = "invoice_%d.pdf" %(123)
             content = "inline;filename='%s'" %(filename)
             response ['Content-Disposition']=content
             return response
        else:
            return HttpResponse("Not Found")
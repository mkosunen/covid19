"""
========
Covid19
========

Covid19 modeling environment using TheSydeKick system modeling framework

Current docstring documentation style is Numpy
https://numpydoc.readthedocs.io/en/latest/format.html

Initially written by Marko Kosunen, 2020.

"""

import os
import sys
if not (os.path.abspath('../../thesdk') in sys.path):
    sys.path.append(os.path.abspath('../../thesdk'))

import subprocess

from thesdk import *
from numpy.polynomial import Polynomial
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pdb

class covid19(thesdk):
    @property
    def _classfile(self):
        return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__

    def __init__(self,*arg): 
        self.print_log(type='I', msg='Inititalizing %s' %(__name__))
        #self.proplist=['figtype']
        self_countries=['Finland']
        #if len(arg)>=1:
        #    parent=arg[0]
        #    self.copy_propval(parent,self.proplist)
        #    self.parent =parent;
        ##self.init()

    @property
    def punchline(self):
        if not hasattr(self,'_punchline'):
            self._punchline="\nCovid cases in %s"
        return self._punchline

    @property
    def recovery_time(self):
        if not hasattr(self,'_recovery_time'):
            self._recovery_time=17
        return self._recovery_time

    @punchline.setter
    def punchline(self,val):
        self._punchline=val
        return self._punchline

    @property
    def countries(self):
        if not hasattr(self,'_countries'):
            self._countries=['Finland']
        return self._countries

    @countries.setter
    def countries(self,val):
        self._countries=val
        return self._countries

    @property
    def declinelevel(self):
        if not hasattr(self,'_declinelevel'):
            self._declinelevel=0.1
        return self._declinelevel

    @declinelevel.setter
    def declinelevel(self,val):
        self._declinelevel=val
        return self._declinelevel

    @property
    def countrydata(self):
        if not hasattr(self,'_countrydata'):
            self._countrydata={key: country(name=key) for key in self.countries }
        return self._countrydata
    @property
    def figurepath(self):
        self._figurepath=self.entitypath+'/Figures'
        return self._figurepath

    def plot(self):
        hfont = {'fontname':'Sans'}
        figure,axes = plt.subplots(2,1,sharex=True,figsize=(10,12))
        #figure,axes = plt.subplots(2,1,sharex=True)
        refline=np.ones(list(self.countrydata.values())[0].relgrowthrate.size)*self.declinelevel
        #axes[0].plot(refline,linewidth=3,color='g')
        for key,val in self.countrydata.items():
            val.figtype=self.figtype
            axes[0].plot(val.relgrowthratefive,label=val.name,linewidth=2)
            axes[1].plot(val.active,label=val.name,linewidth=2)
            axes[0].set_ylabel("Relative increase\n5-day avg", **hfont,fontsize=18);
            axes[1].set_ylabel('Active cases\n past %s d' %(self.recovery_time), **hfont,fontsize=18);
            axes[1].set_xlabel('Days since Jan 20, 2020', **hfont,fontsize=18);
            axes[0].set_xlim(0,val.active.size-1)
            axes[1].set_xlim(0,val.active.size-1)
        axes[0].legend()
        axes[0].set_ylim(0,1)
        axes[1].legend()
        axes[0].grid(True)
        axes[1].grid(True)
        titlestr = self.punchline %('selected countries')
        plt.subplots_adjust(top=0.8)
        plt.subplots_adjust(left=0.2)
        plt.suptitle(titlestr,fontsize=20);
        #plt.subplots_adjust(hspace=0.4)
        plt.grid(True);
        printstr=self.figurepath+"/Covid19_Selected_cases."+self.figtype
        plt.show(block=False);
        figure.savefig(printstr, format=self.figtype, dpi=300);

        for key,val in self.countrydata.items():
            val.plot()

    def plot_estimated_recovery_times(self):
        for key,val in self.countrydata.items():
            val.figtype=self.figtype
            val.plot_estimated_recovery_time()



    @property
    def databasefiles(self): 
        self._databasefiles={ key : self.entitypath+'/database/'+key+'.csv' for key in [ 'Confirmed', 'Deaths', 'Finland_Confirmed' ] }
        return self._databasefiles

    @property
    def _classfile(self):
         return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__
    def download(self):
        '''Downloads the case databases'''
        for key,value in self.databasefiles.items():
            if key is not 'Finland_Confirmed' :
                #command= 'wget "https://raw.github.com/mkosunen/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_'+key.lower()+'_global.csv" -O '+ value
                command= 'wget "https://raw.github.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_'+key.lower()+'_global.csv" -O '+ value
            elif key is 'Finland_Confirmed':
                command= 'wget "https://sampo.thl.fi/pivot/prod/fi/epirapo/covid19case/fact_epirapo_covid19case.csv?column=dateweek2020010120201231-443702L" -O '+ value
            self.print_log(type='I', msg='Executing %s \n' %(command))
            subprocess.check_output(command, shell=True);

    def read(self,**kwargs):
        ''' Read by country '''
        country=kwargs.get('country','Finland')
        cases=kwargs.get('type','Confirmed')
        fid=open(self.databasefiles[cases],'r')
        readd = pd.read_csv(fid,dtype=object,sep=',',header=None)
        readd=readd[(readd[1].str.match(country))]
        #if country is 'Finland' and cases is 'Confirmed':
        #    fid=open(self.databasefiles['Finland_Confirmed'],'r')
        #    readd = pd.read_csv(fid,dtype=object,sep=';').fillna('0')
        #    readd=readd.set_index('Aika')
        #    enddate=str((pd.datetime.now()-pd.Timedelta(days=1)).date())
        #    dat=np.array(readd.loc['2020-01-22':enddate].transpose().astype('int'))
        #    #dat=np.cumsum(np.r_[0, dat[0,:]])
        #    dat=np.cumsum(dat[0,:])
        #    fid.close()
        if country is not 'China':
            dat=readd[~(readd[0].str.match('',na=False))]
            dat=np.sum(np.array(dat.values[:,4:].astype('int')),axis=0)
        else:
            dat=readd
            dat=np.sum(np.array(dat.values[:,4:].astype('int')),axis=0)
        fid.close()
        return dat

class country(covid19):
    '''Class for country data'''

    def __init__(self,**kwargs):
        self._name=kwargs.get('name','Finland')
    
    @property
    def name(self):
        return self._name
    
    @property
    def figtype(self):
        if not hasattr(self,'_figtype'):
            self._figtype='eps'
        return self._figtype

    @figtype.setter
    def figtype(self,val):
            self._figtype=val


    @property
    def confirmed(self):
        if not hasattr(self,'_confirmed'):
            self._confirmed=self.read(country=self._name,type='Confirmed')
        return self._confirmed

    @property
    def recovered(self):
        if not hasattr(self,'_recovered'):
            country=self.name
            i=self.recovery_time
            filt=np.ones((1,i))[0,:]
            self._recovered=self.confirmed-self.deaths-self.active
        return self._recovered

    @property
    def deaths(self):
        if not hasattr(self,'_deaths'):
            self._deaths=self.read(country=self._name,type='Deaths')
        return self._deaths

    @property
    def relgrowthrate(self):
        prevact=np.r_[0,self.active[0:-1]]
        zs=np.where(prevact==0)
        relact=prevact
        relact[zs]=1
        if not hasattr(self,'_relgrowthrate'):
            self._relgrowthrate=np.diff(np.r_[ 0, self.confirmed])/relact
        return self._relgrowthrate

    @property
    def relgrowthratefive(self):
        prevact=np.r_[0,self.active[0:-1]]
        zs=np.where(prevact==0)
        relact=prevact
        relact[zs]=1
        d=np.diff(np.r_[ 0, self.confirmed])
        filt=np.ones((1,5))[0,:]
        awgd=(np.convolve(filt,d/relact))[0:-4]/filt.size
        if not hasattr(self,'_relgrowthratefove'):
            self._relgrowthratefive=awgd
        return self._relgrowthratefive

    @property
    def growth(self):
        if not hasattr(self,'_growth'):
            self._growth=np.diff(np.r_[0, (self.confirmed-self.deaths)])
        return self._growth

    @property
    def active(self):
        if not hasattr(self,'_active'):
            country=self.name
            i=self.recovery_time
            filt=np.ones((1,i))[0,:]
            self._active=np.convolve(filt,np.diff(np.r_[0, (self.confirmed-self.deaths)]))[0:-(i-1)]
        return self._active

    def estimate_recovery_time(self):
        country=self.name
        files={'Confirmed': self.entitypath+"/database/Confirmed.csv.backup_23.3.2020",
                'Deaths': self.entitypath+"/database/Deaths.csv.backup_23.3.2020",
                'Recovered': self.entitypath+"/database/Recovered.csv.backup_23.3.2020"}

        Data={}
        for key,file in files.items():
            fid=open(file,'r')
            dat1 = pd.read_csv(fid,dtype=object,sep=',',header=None)
            dat2 = dat1[dat1[1].str.match(country)]
            Data[key]=np.sum(np.array(dat2.values[:,4:-1].astype('int')),axis=0)

        Data['Active']= Data['Confirmed']-Data['Deaths']-Data['Recovered']
        #for i in range(5,26):
        Data['Error']=[]
        Data['Estimated']={}
        for i in range(10,25):
            filt=np.ones((1,i))[0,:]
            Data['Estimated'][i]=np.convolve(filt,np.diff(np.r_[0, (Data['Confirmed']-Data['Deaths'])]))[0:-(i-1)]
            errorvar=np.sum((np.log(Data['Active'])-np.log(Data['Estimated'][i])**2))/len(Data['Active']-1)
            Data['Error'].append((i,errorvar))
        mindata=min(Data['Error'], key = lambda t : t[1])
        self.estimated_recovery_data=Data
        self.estimated_recovery_time=mindata

    def plot_estimated_recovery_time(self):
        self.estimate_recovery_time()
        hfont = {'fontname':'Sans'}
        figure,axes = plt.subplots()
        #figure,axes = plt.subplots(2,1,sharex=True)
        axes.plot(self.estimated_recovery_data['Estimated'][self.estimated_recovery_time[0]],linewidth=2,label='Estimated')
        axes.plot(self.estimated_recovery_data['Active'],linewidth=2,label='Reported')
        titlestr = "Active cases in %s \n Best fit recovery time %s days" %(self.name,self.estimated_recovery_time[0])
        axes.set_ylabel('Active cases' , **hfont,fontsize=18);
        axes.set_xlabel('Days since Jan 20, 2020', **hfont,fontsize=18);
        axes.legend()
        axes.grid(True)
        plt.suptitle(titlestr,fontsize=20);
        plt.grid(True);
        plt.subplots_adjust(top=0.8)
        printstr=self.figurepath+"/Covid19_Recovery_in_%s.%s" %(self.name,self.figtype)
        plt.show(block=False);
        figure.savefig(printstr, format=self.figtype, dpi=300);

    def plot(self):
        hfont = {'fontname':'Sans'}
        figure,axes = plt.subplots(4,1,sharex=False,figsize=(6,10))
        refline=np.ones(list(self.countrydata.values())[0].relgrowthrate.size)*self.declinelevel
        #axes[0].plot(refline,linewidth=3,color='g')
        axes[0].plot(self.relgrowthrate,label="Relative increrase")
        axes[0].plot(self.relgrowthratefive,label='5-day average')
        axes[1].plot(self.active,label='Active cases')
        axes[2].plot([i for i in range(-self.recovery_time+1,1)],self.growth[-self.recovery_time:],label='Growth')
        #Do linear fit
        time=np.arange(-self.recovery_time+1,1)
        poly=Polynomial.fit(time, self.growth[-self.recovery_time:],1)
        k=poly.coef[1]
        efficiency=(poly(time)[0]/poly(time)[-1])
        axes[2].plot(time,poly(time),label='Trend, eff=%s' %('{0:.2f}'.format(efficiency)))
        axes[3].plot(time,self.relgrowthrate[-self.recovery_time:],label='Relative increase')
        axes[3].plot(time,self.relgrowthratefive[-self.recovery_time:],label='5-day average')
        axes[1].axvline(self.active.shape[0]-self.recovery_time,linestyle='dashed', color='c',label='Recovery limit')
        axes[0].set_xlabel('Days since Jan 20, 2020', **hfont,fontsize=18);
        axes[0].set_ylabel('Relative increase', **hfont,fontsize=18);
        axes[1].set_xlabel('Days since Jan 20, 2020', **hfont,fontsize=18);
        axes[1].set_ylabel('Active cases\n past %s d' %(self.recovery_time), **hfont,fontsize=18);
        axes[2].set_xlabel('Active period', **hfont,fontsize=18);
        axes[2].set_ylabel('Daily growth\n past %s d' %(self.recovery_time), **hfont,fontsize=18);
        axes[3].set_xlabel('Active period', **hfont,fontsize=18);
        axes[3].set_ylabel('Relative increase\n past %s d' %(self.recovery_time), **hfont,fontsize=18);
        axes[0].legend()
        axes[1].legend()
        axes[2].legend()
        axes[3].legend()
        axes[0].set_xlim(0,self.active.size-1)
        axes[0].set_ylim(0,1)
        axes[1].set_xlim(0,self.active.size-1)
        axes[2].set_xlim(-self.recovery_time+1,0)
        axes[3].set_xlim(-self.recovery_time+1,0)
        axes[3].set_ylim(0,0.4)
        axes[0].grid(True)
        axes[1].grid(True)
        axes[2].grid(True)
        axes[3].grid(True)
        titlestr = self.punchline %(self.name)
        #plt.subplots_adjust(top=0.8,hspace=0.4)
        plt.subplots_adjust(hspace=0.4)
        plt.subplots_adjust(left=0.2)
        plt.suptitle(titlestr,fontsize=20);
        plt.grid(True);
        printstr=self.figurepath+"/Covid19_in_%s.%s" %(self.name,self.figtype)
        plt.show(block=False);
        figure.savefig(printstr, format=self.figtype, dpi=300);
        plt.show(block=False);

if __name__=="__main__":
    from  covid19 import *
    import pdb

    a=covid19()
    a.download()
    a.figtype='png'
    #a.figtype='eps'
    #print(a.countrydata['Finland'].active)
    a.countries=['Finland', 'Italy', 'Spain', 'France','Germany', 'Austria', 'Sweden', 'Denmark', 'Norway', 'US', 'China', "Korea, South"]
    #a.countries=['Finland' ]
    #a.countries=['Finland', 'Italy', 'Spain', 'France','Germany', 'Sweden', 'Denmark', 'Norway', 'China', "Korea, South"]
    a.plot()
    #a.read_finland()
    #a.plot_estimated_recovery_times()

    input()


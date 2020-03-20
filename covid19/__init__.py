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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
    def countries(self):
        if not hasattr(self,'_countries'):
            self._countries=['Finland']
        return self._countries

    @countries.setter
    def countries(self,val):
        self._countries=val
        return self._countries


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
        for key,val in self.countrydata.items():
            val.figtype=self.figtype
            axes[0].plot(val.relgrowthratefive,label=val.name,linewidth=2)
            axes[1].plot(val.active,label=val.name,linewidth=2)
            axes[0].set_ylabel("Relative growth,\n5-day avg", **hfont,fontsize=18);
            axes[1].set_ylabel('Active cases', **hfont,fontsize=18);
            axes[1].set_xlabel('Days since Jan 20, 2020', **hfont,fontsize=18);
            axes[0].set_xlim(0,val.active.size-1)
            #axes[0].set_ylim(0,1)
            axes[1].set_xlim(0,val.active.size-1)
        axes[0].legend()
        axes[1].legend()
        axes[0].grid(True)
        axes[1].grid(True)
        titlestr = "Covid19 cases in selected coutries"
        plt.suptitle(titlestr,fontsize=20);
        plt.grid(True);
        printstr=self.figurepath+"/Covid19_Selected_cases."+self.figtype
        plt.show(block=False);
        figure.savefig(printstr, format=self.figtype, dpi=300);

        for key,val in self.countrydata.items():
            val.plot()


    @property
    def databasefiles(self): 
        self._databasefiles={ key : self.entitypath+'/database/'+key+'.csv' for key in [ 'Confirmed', 'Recovered', 'Deaths' ] }
        return self._databasefiles

    @property
    def _classfile(self):
         return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__

    def download(self):
        '''Downloads the case databases from Johns Hopkins'''

        for key,value in self.databasefiles.items():
            command= 'wget "https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_19-covid-'+key+'.csv&filename=time_series_2019-ncov-'+key+'.csv" -O '+ value
            print('Executing %s \n' %(command))
            subprocess.check_output(command, shell=True);

    def read(self,**kwargs):
        ''' Read by country '''
        country=kwargs.get('country','Finland')
        cases=kwargs.get('type','Confirmed')
        fid=open(self.databasefiles[cases],'r')
        readd = pd.read_csv(fid,dtype=object,sep=',',header=None)
        dat=readd[readd[1].str.match(country)]
        dat=np.sum(np.array(dat.values[:,4:].astype('int')),axis=0)
        return dat

class country(covid19):
    '''class for area data'''

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
            self._recovered=self.read(country=self._name,type='Recovered')
        return self._recovered

    @property
    def deaths(self):
        if not hasattr(self,'_deaths'):
            self._deaths=self.read(country=self._name,type='Deaths')
        return self._deaths

    @property
    def relgrowthrate(self):
        zs=np.where(self.active==0)
        relact=self.active
        relact[zs]=1
        if not hasattr(self,'_relgrowthrate'):
            self._relgrowthrate=np.diff(np.r_[ 0, self.confirmed])/relact
        return self._relgrowthrate

    @property
    def relgrowthratefive(self):
        zs=np.where(self.active==0)
        relact=self.active
        relact[zs]=1
        d=np.diff(np.r_[ 0, self.confirmed])
        filt=np.ones((1,5))[0,:]
        awgd=(np.convolve(filt,d/relact))[0:-4]/filt.size
        if not hasattr(self,'_relgrowthratefove'):
            self._relgrowthratefive=awgd
        return self._relgrowthratefive

    @property
    def active(self):
        if not hasattr(self,'_active'):
            self._active=self.confirmed-self.recovered-self.deaths
        return self._active

    def plot(self):
        hfont = {'fontname':'Sans'}
        figure,axes = plt.subplots(2,1,sharex=True)
        axes[0].plot(self.relgrowthrate,label='Relative growth')
        axes[0].plot(self.relgrowthratefive,label='5-day average')
        axes[1].plot(self.active,label='Active cases')
        axes[0].set_ylabel('Relative growth', **hfont,fontsize=18);
        axes[1].set_ylabel('Active cases', **hfont,fontsize=18);
        axes[1].set_xlabel('Days since Jan 20, 2020', **hfont,fontsize=18);
        axes[0].legend()
        axes[0].set_xlim(0,self.active.size-1)
        axes[0].set_xlim(0,1)
        axes[1].set_xlim(0,self.active.size-1)
        axes[0].grid(True)
        axes[1].grid(True)
        titlestr = "Covid19 cases in %s" %(self.name)
        plt.suptitle(titlestr,fontsize=20);
        plt.grid(True);
        printstr=self.figurepath+"/Covid19_in_%s.%s" %(self.name,self.figtype)
        plt.show(block=False);
        figure.savefig(printstr, format=self.figtype, dpi=300);
        plt.show(block=False);



if __name__=="__main__":
    from  covid19 import *
    from covid19 import country as co
    import pdb

    a=covid19()
    a.download()
    a.figtype='png'
    a.countries=['Finland', 'Italy', 'Spain', 'Germany', 'Sweden', 'US', 'China', "Korea, South"]
    a.plot()

    input()


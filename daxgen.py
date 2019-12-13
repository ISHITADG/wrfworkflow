#!/usr/bin/env python

import sys
import os
import pwd
import time
from Pegasus.DAX3 import *
from datetime import datetime
from argparse import ArgumentParser

class wrf_workflow(object):
    def __init__(self, outdir, nc_fn):
        self.outdir = outdir
        self.nc_fn = nc_fn

    def generate_dax(self):
        "Generate a workflow"
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        dax = ADAG("casa_wrf_wf-%s" % ts)
        dax.metadata("name", "CASA WRF")

        for f in self.nc_fn:
            f = f.split("/")[-1]
            if f.endswith(".gz"):
                qpefilename = f[:-3]
                unzip = Job("gunzip")
                unzip.addArguments(f)
                zipfile = File(f)
                unzip.uses(zipfile, link=Link.INPUT)
                unzip.uses(qpefilename, link=Link.OUTPUT, transfer=False, register=False)
                dax.addJob(unzip)
            else:
                qpefilename = f;

            string_end = self.nc_fn[-1].find("-")
            file_time = self.nc_fn[-1][string_end+1:string_end+16]
            file_ymd = file_time[0:8]
            file_hms = file_time[9:15]
            file_hm = file_time[9:13]
            #print file_ymd
            #print file_hms
                
            qpefile = File(qpefilename)
            
            wrf_outputfilename = file_ymd + file_hm + "." + CHRTOUT_DOMAIN1;
            wrf_outputfile = File(wrf_outputfilename);
            
            wrf_job = Job("wrf")
            wrf_job.uses(wrf_outputfile, link=Link.OUTPUT, transfer=True, register=False)
            
            dax.addJob(wrf_job)

            # Write the DAX file
            daxfile = os.path.join(self.outdir, dax.name+".dax")
            dax.writeXMLFile(daxfile)
            print daxfile

    def generate_workflow(self):
        # Generate dax
        self.generate_dax()
        
if __name__ == '__main__':
    parser = ArgumentParser(description="Single Hail Workflow")
    parser.add_argument("-f", "--files", metavar="INPUT_FILE", type=str, nargs="+", help="Filename", required=True)
    parser.add_argument("-o", "--outdir", metavar="OUTPUT_LOCATION", type=str, help="DAX Directory", required=True)

    args = parser.parse_args()
    outdir = os.path.abspath(args.outdir)
    
    if not os.path.isdir(args.outdir):
        os.makedirs(outdir)

    workflow = single_hail_workflow(outdir, args.files)
    workflow.generate_workflow()

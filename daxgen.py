#!/usr/bin/env python

import sys
import os
import pwd
import time
from Pegasus.DAX3 import *
from datetime import datetime
from argparse import ArgumentParser

class wrf_workflow(object):
    def __init__(self, outdir, qpe_tarball, wrf_config):
        self.outdir = outdir
        self.qpe_tarball = qpe_tarball
        self.wrf_config = wrf_config

    def generate_dax(self):
        "Generate a workflow"
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        dax = ADAG("casa_wrf_wf-%s" % ts)
        dax.metadata("name", "CASA WRF")

        f = self.qpe_tarball.split("/")[-1]
        if f.endswith(".gz"):
            qpetarball_fn = self_qpetarball[:-3]
            unzip = Job("gunzip")
            unzip.addArguments(qpetarball_fn)
            zipfile = File(qpetarball_fn)
            unzip.uses(zipfile, link=Link.INPUT)
            unzip.uses(qpetarball_fn, link=Link.OUTPUT, transfer=False, register=False)
            dax.addJob(unzip)
        else:
            qpetarball_fn = self.qpe_tarball;

        
        #string_end = self.qpe_tarball[-1].find("-")
        #file_time = self.qpe_tarball[-1][string_end+1:string_end+16]
        #file_ymd = file_time[0:8]
        #file_hms = file_time[9:15]
        #file_hm = file_time[9:13]
        #print file_ymd
        #print file_hms
        
        untardatajob = Job("tar", node_label="untar")
        untardatajob.addArguments("-xf", qpe_tarball, "-C", "/example_case/NWM")
        untardatajob.uses(qpe_tarball, link=Link.INPUT)
        
        untarconfigjob = Job("tar", node_label="untar")
        untarconfigjob.addArguments("-xf", wrf_config, "-C", "/example_case/NWM")
        untarconfigjob.uses(wrf_config, link=Link.INPUT)
        
        #wrf_outputfilename = file_ymd + file_hm + "." + CHRTOUT_DOMAIN1;
        #wrf_outputfile = File(wrf_outputfilename);
            
        wrf_job = Job("wrf")
        #wrf_job.uses(wrf_outputfile, link=Link.OUTPUT, transfer=True, register=False)
            
        dax.addJob(wrf_job)
        dax.depends(wrf_job, untardatajob)
        dax.depends(wrf_job, untarconfigjob)
        #dax.depends(untarjob, unzip)
        # Write the DAX file
        daxfile = os.path.join(self.outdir, dax.name+".dax")
        dax.writeXMLFile(daxfile)
        print daxfile

    def generate_workflow(self):
        # Generate dax
        self.generate_dax()
        
if __name__ == '__main__':
    parser = ArgumentParser(description="WRF Workflow")
    parser.add_argument("-f", "--qpe_tarball", metavar="qpe_tarball", type=str, nargs="+", help="qpe_tarball", required=True)
    parser.add_argument("-c", "--wrf_config", metavar="wrf_config", type=str, nargs="+", help="wrf_config", required=True)
    parser.add_argument("-o", "--outdir", metavar="OUTPUT_LOCATION", type=str, help="DAX Directory", required=True)

    args = parser.parse_args()
    outdir = os.path.abspath(args.outdir)
    
    if not os.path.isdir(args.outdir):
        os.makedirs(outdir)

    workflow = wrf_workflow(outdir, args.qpe_tarball, args.wrf_config)
    workflow.generate_workflow()

import os
import argparse
from argparse import ArgumentParser
import time
import datetime
import json
import libtmux


VERSION=1.0

class Automation():

    def __init__(self, args):
        self.args = args
        self.output_dir=self.args.output_dir
        self.work_dir=self.args.work_dir
        self.iteration=self.args.iteration
        self.test=self.args.test
        self.summary_name=self.args.summary_name
        self.emon=self.args.emon
        self.emon_dir=""
        self.log_dir=""
        self.command=""
        self.dir=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') 
        self.dsa=self.args.dsa

    def date_logs(self):
        path=os.path.join(self.output_dir,self.dir)
        self.log_dir=path    
        try:  
            os.makedirs(path) 
            print(path,"created for output logs")  
        except OSError as error:  
            print(path,"Directory already exist !!") 

    def read_json(self):
        with open(self.test) as f:
          self.json_data = json.load(f)
          var=""
          for iteration in range(1,self.iteration+1,1):
            for index in self.json_data:
              for work in index["work"]:
                for queuedepth in index["queuedepth"]:
                  for thread in index["thread"]:
                    for cpumask in index["cpumask"]:
                      for transfer in index["transfer"]:
                        for memory in index["memory"]:
                          for batch in index["batch"]:
                              print("work :",work)
                              print("queuedepth :",queuedepth)
                              print("thread :",thread)
                              print("cpumask :",cpumask)
                              print("transfersize :",transfer)
                              print("memory :",memory)
                              print("batch :",batch)
                              if memory == "LLC":
                                var="-prd"
                              else:
                                var=" " 
                              cpu_flag=" -m -fc" 
                              name = "software_" 
                              if self.dsa:  
                                cpu_flag=" -fcj  "
                                name = "hardware_"
                              self.emon_dir=str(name)+str(work)+"_"+str(queuedepth)+"_"+str(transfer)+"_"+str(cpumask)+"_"+str(thread)+"_"+str(index["time"])+"_"+str(iteration)+"_"+str(memory)+"_"+str(batch)
                              print("emon dir : ",self.emon_dir)
                              log_name=self.log_dir+"/"+self.emon_dir
                              self.command="-o"+str(work)+" -n"+str(queuedepth)+" -s"+str(transfer)+" -k"+str(cpumask)+" -i"+str(index["time"])+" -g3"+str(cpu_flag)+str(var)+" 2>&1 | tee "+log_name+".txt;" 
                              #print(self.command)
                              
                              print(self.work_dir+'/./src/dsa_micros '+self.command)
                              if self.emon:
                                os.makedirs("./emon/"+str(self.dir)+"/"+self.emon_dir)
                              Automation.run_session()
      

             
    def run_session(self):
        print('-'*80)       
        os.system("cd "+self.work_dir)
        #print(self.data)
        server = libtmux.Server()
        session = server.new_session(session_name="session_test", kill_session=True, attach=False)
        session = server.find_where({"session_name": "session_test"})
        window = session.new_window(attach=True, window_name="session_test")
        pane1 = window.attached_pane
        pane2 = window.split_window(vertical=True) 
        window.select_layout('tiled')

        #time.sleep(3)
        if self.emon:
         pane1.send_keys('timeout 45 ./../dsa_micros/src/dsa_micros '+self.command)
         pane2.send_keys('timeout 40 python2 emon.py -w '+str(self.dir)+"/"+self.emon_dir)
         pane1.send_keys('sleep 60')
        else :
         pane1.send_keys('./../dsa_micros/src/dsa_micros '+self.command)
         pane1.send_keys('sleep 5')

        pane1.send_keys('tmux kill-session -t session_test')
        server.attach_session(target_session="session_test")
        #time.sleep(3)
    def summary(self):
        print("you can find logs in :",self.log_dir)
        cmd="grep -r 'GB per sec ='"+self.log_dir+" | awk '{print $1","$5}' > "+self.log_dir+"/summary.txt"
        print(cmd)
        os.system(cmd)
        os.system("grep -vwE 'GB:' "+self.log_dir+"/summary.txt | sed 's/:/,/Ig' | sed 's/_/,/Ig' > "+self.log_dir+"/summary.csv")
        os.system("python3 Sheet_transformer_micro.py -p "+self.log_dir+"/")

    def Activate_setup(self):
        print("Activating the Setup")
        #os.system("sudo ./../dsa_micros/setup_dsa.sh configs/4e1w-d.conf ")

       
if __name__ == "__main__":
    print("Using Automation version :" ,VERSION)
    parser = ArgumentParser()
    parser.add_argument('--output_dir', type=str, default=os.getcwd()+"/logs/micro/", help="directory to save the log")
    parser.add_argument('--work_dir', type=str, default='/root/DSA/dsa_micros', help="working directory path")
    parser.add_argument('--test', type=str, default='./config/emon_config.json',help="name of the configuration tests file")
    parser.add_argument('--iteration', type=int, default=1,help="number of iteration you want to run")
    parser.add_argument('--emon', type=bool, default=False,help="name for the final summary file")
    parser.add_argument('--summary_name', type=str, default="summary.csv",help="name for the final summary file")
    parser.add_argument('--dsa', type=bool, default=True,help="select DSA vs CPU")
    args = parser.parse_args()
    Automation=Automation(args)
    Automation.date_logs()
    Automation.Activate_setup()
    Automation.read_json()
    #Automation.summary()
 

 


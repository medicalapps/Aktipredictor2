import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import csv
import time
from datetime import datetime, timedelta
import datetime as dt
import matplotlib.dates as mdates
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm

import matplotlib.dates as mdates
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
from matplotlib.ticker import AutoMinorLocator


from multiprocessing import Pool

class plotter():
    def __init__(self):
        super(plotter, self).__init__()
    
        
        self.figs={}
        self.comps = {}
        self.axs={}
        self.cids = {}
        self.accuracy = {}
        self.Last_pred_first_index = {}
        self.avrage_pred = []
        self.triggerTime = datetime.now()
        self.inspecting = False


   
    def onclick(self, event):
        if(self.inspecting):
            self.inspecting =  False
        else:
            self.inspecting = True

    
    def plotresults(self, first_run, run_epoch):
        my_dpi = 100
   
        # True_Answers = open(SettingsObject.TrueAnswersfile)
        # Prediction_Answers = open(SettingsObject.PredictionAnswersfile)
        # Training_Answers = open(SettingsObject.TrainingAnswersfile)
        labeldata_longitud = {}
        training_longitud = {}
        prediction_longitud = {}
        labelCounter = 0
        with open('Answers_network_2022-08-18 11-02-04_155053.csv', newline='') as True_Answers:
            True_Answers_reader = csv.reader(True_Answers, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            #row = row.replace("'", "").replace('\n', '')
            for row in True_Answers_reader:
                labelCounter = labelCounter +1
                for index, value in enumerate(row):
                    if not index in labeldata_longitud:
                        labeldata_longitud[index] = []
                    labeldata_longitud[index].append(value)
                    totalgraphs = index
                    
            for index in labeldata_longitud:
                labeldata_longitud[index] = labeldata_longitud[index][:-2]
 
            
        True_Answers.close()
        trainingCounter = 0       
        with open('TrainingAnswersfile.csv', newline='') as Training_Answers:
            Training_Answers_reader = csv.reader(Training_Answers, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            #row = row.replace("'", "").replace('\n', '')
            for row in Training_Answers_reader:
                trainingCounter = trainingCounter + 1
                for index, value in enumerate(row):
                    if not index in training_longitud:
                        training_longitud[index] = []
                    training_longitud[index].append(value)
                totalgraphs = index
        Training_Answers.close()
        # predictionCounter = 0
        # with open(SettingsObject.PredictionAnswersfile, newline='') as Prediction_Answers:
        #     Prediction_Answers_reader = csv.reader(Prediction_Answers, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        #     #row = row.replace("'", "").replace('\n', '')
        #     for row in Prediction_Answers_reader:
        #         predictionCounter = predictionCounter +1
        #         for index, value in enumerate(row):
        #             if not index in prediction_longitud:
        #                 prediction_longitud[index] = []
        
        #             prediction_longitud[index].append(value)
        
        #         totalgraphs = index
        # Prediction_Answers.close()
        # tagetnames = []
        # targetsCounter = 0
        # with open(SettingsObject.Targetsfile, newline='') as Targets:
        #     Targets_reader = csv.reader(Targets, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        #     #row = row.replace("'", "").replace('\n', '')
        #     for row in Targets_reader:
        #         targetsCounter = targetsCounter +1
        #         for index, name in enumerate(row):
        #             tagetnames.append(name)
        # Targets.close()
        # TrainingLog_date_counter = 0
        # DataDateSpan = []
        # PredDateSpan =[]
        # with open(SettingsObject.Traininglog, newline='') as SettingsObject.Traininglog:
        #     SettingsObject.Traininglog_reader = csv.reader(SettingsObject.Traininglog)
        #     #row = row.replace("'", "").replace('\n', '')
        #     for row in SettingsObject.Traininglog_reader:
        #         if row[0] == 'Date done:' and row[3] == 'OK':
        #             DataDateSpan.append(row[1])
        #             PredDateSpan.append(row[2].split(' ')[1])
        #         TrainingLog_date_counter = TrainingLog_date_counter +1
        # SettingsObject.Traininglog.close()
        # accuracy = []
        # with open(SettingsObject.Lossfile, newline='') as SettingsObject.Lossfile_read:
        #     accuracy_line = SettingsObject.Lossfile_read.readline()
        #     accuracy_line.replace("'", "")
        #     accuracy_splits = accuracy_line.split(',')
        #     for part in accuracy_splits:
        #         accuracy.append(float(part))
        #     #SettingsObject.Lossfile_reader = csv.reader(SettingsObject.Lossfile_read)
        #     #row = row.replace("'", "").replace('\n', '')
        #     #SettingsObject.Lossfile_reader
     
        # SettingsObject.Lossfile_read.close()
        
        trainingdiff = []
        with open('trainingdiff.csv', newline='') as trainingdifffile_read:
            accuracy_line = trainingdifffile_read.readline()
            accuracy_line.replace("'", "")
            accuracy_splits = accuracy_line.split(',')
            for part in accuracy_splits:
                trainingdiff.append(float(part))
            #SettingsObject.Lossfile_reader = csv.reader(SettingsObject.Lossfile_read)
            #row = row.replace("'", "").replace('\n', '')
            #SettingsObject.Lossfile_reader
     
        trainingdifffile_read.close()

        predictiondiff = []
        with open('validationloss.csv', newline='') as validationdifffile_read:
            accuracy_line = validationdifffile_read.readline()
            accuracy_line.replace("'", "")
            accuracy_splits = accuracy_line.split(',')
            for part in accuracy_splits:
                predictiondiff.append(float(part))
            #SettingsObject.Lossfile_reader = csv.reader(SettingsObject.Lossfile_read)
            #row = row.replace("'", "").replace('\n', '')
            #SettingsObject.Lossfile_reader
     
        validationdifffile_read.close()
        
        #labelspace = np.linspace(0, len(labeldata) - 1) 
        #print(f'preditionspaceSpace {preditionspaceSpace} Predictioncounter: {predictionCounter} TrainingCounter: {trainingCounter} TrueCounter: {trueAnswerCounter}')
        sqrcount = int(np.sqrt(totalgraphs)+1)
        colwidth = int(1980/(sqrcount))
        rowheight = int(1000/(sqrcount)) 
        width = int(colwidth *0.9)
        height = int(rowheight *0.8)
        px = 1/my_dpi 


        
        for idx in range(totalgraphs+1):
            
            if not idx in self.figs:
                self.figs[idx]=plt.figure(figsize=(width*px, height*px))
            else:
                self.figs[idx].clear()
            if (first_run):
                
                rowindex = int(idx/sqrcount)*rowheight
                colindex = int(idx%sqrcount)*colwidth
                # mngr = plt.get_current_fig_manager()äö
                # mngr.window.setGeometry(colindex,rowindex,6,5)
                backend = matplotlib.get_backend()
                if backend == 'TkAgg':
                    self.figs[idx].canvas.manager.window.wm_geometry("+%d+%d" % (colindex,rowindex ))
                elif backend == 'WXAgg':
                    self.figs[idx].canvas.manager.window.SetPosition((colindex, rowindex))
                else:
                    # This works for QT and GTK
                    # You can also use window.setGeometry
                    self.figs[idx].canvas.manager.window.move(colindex, rowindex)
                    


                self.cids[idx] = self.figs[idx].canvas.mpl_connect('resize_event', self.onclick)
                self.inspecting = False
            #self.figs[idx].set_size_pi
            self.axs[idx]=self.figs[idx].add_subplot(111)
            
            #self.axs[idx].plot(training_longitud[idx], color = 'blue', linewidth=2 )
            
            labellen = len(labeldata_longitud[idx])
            predlen = len(prediction_longitud[idx])
            trainlen = len(training_longitud[idx])
            lookback = predlen

            # firsttrainingDay =  datetime.strptime(DataDateSpan[0], "%Y-%m-%d")
            # lasttrainday = datetime.strptime(PredDateSpan[-1], "%Y-%m-%d") +  timedelta(days=trainlen)
            
            # traindays = mdates.drange(firsttrainingDay,  lasttrainday, datetime.timedelta(days=1))

            #self.figs[idx].gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            #self.figs[idx].gca().xaxis.set_major_locator(mdates.DayLocator(interval=28))
            lookbackmultiplier = 1
            
            # validSpace = np.linspace(int(trainlen), int(labellen-1), num=(labellen)-(trainlen))
            
            # PredictionSpace = np.linspace(int(labellen), int(labellen+(predlen-validSpace.size-1)), num=(predlen-validSpace.size)) 
             
            # trainspace = np.linspace(int(trainlen-(lookbackmultiplier*lookback)),int(trainlen-1), num=((trainlen)-(trainlen-(lookbackmultiplier*lookback))))
            # labelspace = np.linspace(int(labellen-(lookbackmultiplier*lookback)+SettingsObject.lookToTheFuture),int(labellen-1), num=(validSpace.size) )
        
            # predictionslice =  prediction_longitud[idx][validSpace.size:]
            # validslice = prediction_longitud[idx][0:validSpace.size]
            # labelslice = labeldata_longitud[idx][int(validSpace[0]):]
            #trainingslice = training_longitud[idx][int(trainspace[0]):]
    

            #titel =str(tagetnames[idx])
      

            
            # if (run_epoch%2 == 0):

            #     self.axs[idx].plot(labelspace, labelslice, linewidth=1)
            #     #self.axs[idx].plot(trainspace, trainingslice, color = 'blue', linewidth=1)
                
            #     self.axs[idx].plot(validSpace, validslice, linewidth=1)
            #     self.axs[idx].plot(PredictionSpace, predictionslice, linewidth=1)
            #     self.axs[idx].axhline(0, color='k', ls='--', linewidth=1)
            #     self.axs[idx].axvline(trainlen, color='k', ls='--', linewidth=1)
            #else:
            self.axs[idx].plot(labeldata_longitud[idx],linewidth=1)
            self.axs[idx].plot(prediction_longitud[idx], linewidth=1)
            self.axs[idx].plot(training_longitud[idx], linewidth=1)
            self.axs[idx].axhline(0, color='k', ls='--', linewidth=1)
            self.axs[idx].axvline(trainlen, color='k', ls='--', linewidth=1)
            self.axs[idx].set_title(titel)
            self.axs[idx].legend(loc="upper left")
            self.axs[idx].set_facecolor('#EBEBEB')
            # Remove border around plot.
            [self.axs[idx].spines[side].set_visible(False) for side in self.axs[idx].spines]
            # Style the grid.
            self.axs[idx].grid(which='major', color='white', linewidth=1.2)
            self.axs[idx].grid(which='minor', color='white', linewidth=0.6)
            # Show the minor ticks and grid.
            self.axs[idx].minorticks_on()
            # Now hide the minor ticks (but leave the gridlines).
            self.axs[idx].tick_params(which='minor', bottom=False, left=False)

            # Only show minor gridlines once in between major gridlines.
            self.axs[idx].xaxis.set_minor_locator(AutoMinorLocator(2))
            self.axs[idx].yaxis.set_minor_locator(AutoMinorLocator(2))
            self.axs[idx].grid(True)
            
        #     self.comps[idx] = []
        #     self.accuracy[idx] = {'pos_correct': 0, 'neg_correct': 0, 'pos_error': 0, 'neg_error': 0, }
        Avrage = {}  
        Avrage['prediction_longitud'] = {}
        Avrage['training_longitud'] = {}
        Avrage['labeldata_longitud'] = {}
        Avrage['prediction_longitud']['summed'] = []
        Avrage['training_longitud']['summed'] = []
        Avrage['labeldata_longitud']['summed'] = []
        Avrage['prediction_longitud']['avrage'] = []
        Avrage['training_longitud']['avrage'] = []
        Avrage['labeldata_longitud']['avrage'] = []

        for idx in range(totalgraphs+1):
            for index in range(len(prediction_longitud[idx])):
                if idx == 0:
                    Avrage['prediction_longitud']['summed'].append(prediction_longitud[idx][index])
                else:
                    Avrage['prediction_longitud']['summed'][index]  = Avrage['prediction_longitud']['summed'][index] + prediction_longitud[idx][index]
            for index in range(len(training_longitud[idx])):
                if idx == 0:
                    Avrage['training_longitud']['summed'].append(training_longitud[idx][index])
                else:
                    Avrage['training_longitud']['summed'][index]  = Avrage['training_longitud']['summed'][index] + training_longitud[idx][index]
            for index in range(len(labeldata_longitud[idx])):
                if idx == 0:
                    Avrage['labeldata_longitud']['summed'].append(labeldata_longitud[idx][index])
                else:
                    Avrage['labeldata_longitud']['summed'][index]  = Avrage['labeldata_longitud']['summed'][index] + labeldata_longitud[idx][index]
            
        for index in range(len(Avrage['prediction_longitud']['summed'])):
            Avrage['prediction_longitud']['avrage'].append(Avrage['prediction_longitud']['summed'][index]/(idx+1))
        for index in range(len(training_longitud[idx])):
            Avrage['training_longitud']['avrage'].append(Avrage['training_longitud']['summed'][index] /(idx+1))
        for index in range(len(labeldata_longitud[idx])):
            Avrage['labeldata_longitud']['avrage'].append(Avrage['labeldata_longitud']['summed'][index]  /(idx+1))
    
        if not 'avrage' in self.figs:
                self.figs['avrage']=plt.figure(figsize=(width*px, height*px))
        else:
            self.figs['avrage'].clear()
        if (first_run):
            
            rowindex = int((totalgraphs+1)/sqrcount)*rowheight
            colindex = int((totalgraphs+1)%sqrcount)*colwidth
            # mngr = plt.get_current_fig_manager()äö
            # mngr.window.setGeometry(colindex,rowindex,6,5)
            backend = matplotlib.get_backend()
            if backend == 'TkAgg':
                self.figs['avrage'].canvas.manager.window.wm_geometry("+%d+%d" % (colindex,rowindex ))
            elif backend == 'WXAgg':
                self.figs['avrage'].canvas.manager.window.SetPosition((colindex, rowindex))
            else:
                # This works for QT and GTK
                # You can also use window.setGeometry
                self.figs['avrage'].canvas.manager.window.move(colindex, rowindex)
                


            self.cids['avrage'] = self.figs['avrage'].canvas.mpl_connect('resize_event', self.onclick)
            self.inspecting = False
        #self.figs[idx].set_size_pi
        self.axs['avrage']=self.figs['avrage'].add_subplot(111)
        
        #self.axs[idx].plot(training_longitud[idx], color = 'blue', linewidth=2 )
        
        labellen = len(Avrage['labeldata_longitud']['avrage'])
        predlen = len(Avrage['prediction_longitud']['avrage'])
        trainlen = len(Avrage['training_longitud']['avrage'])
        

        # firsttrainingDay =  datetime.strptime(DataDateSpan[0], "%Y-%m-%d")
        # lasttrainday = datetime.strptime(PredDateSpan[-1], "%Y-%m-%d") +  timedelta(days=trainlen)
        
        # traindays = mdates.drange(firsttrainingDay,  lasttrainday, datetime.timedelta(days=1))

        #self.figs[idx].gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        #self.figs[idx].gca().xaxis.set_major_locator(mdates.DayLocator(interval=28))
        lookbackmultiplier = 1
        
        # validSpace = np.linspace(int(trainlen), int(labellen-1), num=(labellen)-(trainlen))
        
        # PredictionSpace = np.linspace(int(labellen), int(labellen+(predlen-validSpace.size-1)), num=(predlen-validSpace.size)) 
            
        # #trainspace = np.linspace(int(trainlen-(lookbackmultiplier*lookback)),int(trainlen-1), num=((trainlen)-(trainlen-(lookbackmultiplier*lookback))))
        # labelspace = np.linspace(int(labellen-(lookbackmultiplier*lookback)+SettingsObject.lookToTheFuture),int(labellen-1), num=(validSpace.size) )
    
    

        # predictionslice =  Avrage['prediction_longitud']['avrage'][validSpace.size:]
        # validslice = Avrage['prediction_longitud']['avrage'][0:validSpace.size]
        # labelslice = Avrage['labeldata_longitud']['avrage'][int(validSpace[0]):]
        # #trainingslice = training_longitud[idx][int(trainspace[0]):]


        titel =str('Medel')
        self.axs['avrage'].set_title(titel)
        
        # if (run_epoch%2 == 0):
          
            
        #     self.axs['avrage'].plot(labelspace, labelslice , linewidth=1)
        #     self.axs['avrage'].plot(validSpace, validslice, linewidth=1)
        #     self.axs['avrage'].plot(PredictionSpace, predictionslice, linewidth=1)
            
        #     self.axs['avrage'].axhline(0, color='k', ls='--', linewidth=1)
        #     self.axs[idx].axvline(len(Avrage['training_longitud']['avrage']), color='k', ls='--', linewidth=1)
        # else:
        self.axs['avrage'].plot(Avrage['labeldata_longitud']['avrage'], linewidth=1)
        self.axs['avrage'].plot(Avrage['prediction_longitud']['avrage'], linewidth=1)
        
        self.axs['avrage'].plot(Avrage['training_longitud']['avrage'],linewidth=1)
        self.axs['avrage'].axhline(0, color='k', ls='--', linewidth=1)
        self.axs['avrage'].axvline(len(Avrage['training_longitud']['avrage']), color='k', ls='--', linewidth=1)
        self.axs['avrage'].set_title(titel)
        self.axs['avrage'].legend(loc="upper left")
        self.axs['avrage'].set_facecolor('#EBEBEB')
        # Remove border around plot.
        [self.axs['avrage'].spines[side].set_visible(False) for side in self.axs[idx].spines]
        # Style the grid.
        self.axs['avrage'].grid(which='major', color='white', linewidth=1.2)
        self.axs['avrage'].grid(which='minor', color='white', linewidth=0.6)
        # Show the minor ticks and grid.
        self.axs['avrage'].minorticks_on()
        # Now hide the minor ticks (but leave the gridlines).
        self.axs['avrage'].tick_params(which='minor', bottom=False, left=False)

        # Only show minor gridlines once in between major gridlines.
        self.axs['avrage'].xaxis.set_minor_locator(AutoMinorLocator(2))
        self.axs['avrage'].yaxis.set_minor_locator(AutoMinorLocator(2))
        self.axs['avrage'].grid(True)


        if not 'acc' in self.figs:
                self.figs['acc']=plt.figure(figsize=(width*px, height*px))
        else:
            self.figs['acc'].clear()
        if (first_run):
            
            rowindex = int((totalgraphs+1)/sqrcount)*rowheight
            colindex = int((totalgraphs+2)%sqrcount)*colwidth
            # mngr = plt.get_current_fig_manager()äö
            # mngr.window.setGeometry(colindex,rowindex,6,5)
            backend = matplotlib.get_backend()
            if backend == 'TkAgg':
                self.figs['acc'].canvas.manager.window.wm_geometry("+%d+%d" % (colindex+110,rowindex+110 ))
            elif backend == 'WXAgg':
                self.figs['acc'].canvas.manager.window.SetPosition((colindex+110,rowindex+110 ))
            else:
                # This works for QT and GTK
                # You can also use window.setGeometry
                self.figs['acc'].canvas.manager.window.move(colindex+110,rowindex+110)
                


            self.cids['acc'] = self.figs['acc'].canvas.mpl_connect('resize_event', self.onclick)
            self.inspecting = False
        #self.figs[idx].set_size_pi
        self.axs['acc']=self.figs['acc'].add_subplot(111)
        
       
        titel =str('Accuracy')
        self.axs['acc'].set_title(titel)
        
        #self.axs['acc'].plot(accuracy, linewidth=1, label='Acc')
        self.axs['acc'].plot(trainingdiff, linewidth=1, label='Train') 
        self.axs['acc'].plot(predictiondiff, linewidth=1,  label='Pred')
        self.axs['acc'].set_title(titel)
        self.axs['acc'].legend(loc="upper left")
        self.axs['acc'].set_facecolor('#EBEBEB')
        # Remove border around plot.
        [self.axs['acc'].spines[side].set_visible(False) for side in self.axs[idx].spines]
        # Style the grid.
        self.axs['acc'].grid(which='major', color='white', linewidth=1.2)
        self.axs['acc'].grid(which='minor', color='white', linewidth=0.6)
        # Show the minor ticks and grid.
        self.axs['acc'].minorticks_on()
        # Now hide the minor ticks (but leave the gridlines).
        self.axs['acc'].tick_params(which='minor', bottom=False, left=False)

        # Only show minor gridlines once in between major gridlines.
        self.axs['acc'].xaxis.set_minor_locator(AutoMinorLocator(2))
        self.axs['acc'].yaxis.set_minor_locator(AutoMinorLocator(2))
        self.axs['acc'].grid(True)
         
        plt.pause(1)
     
        
        return

    def plot(self):
        first_run = True
        self.triggerTime = datetime.now()
        run_epoch = 0

        while True:
            try:
                print(f'self.inspecting: {self.inspecting}')
                if self.inspecting is False:    
                    if datetime.now() > self.triggerTime:
                        self.triggerTime = datetime.now() + timedelta(seconds=0.5)
                    else:
                        plt.pause(1)
                        continue 
                    
                    
                    print(f'Plot Epoch {run_epoch} first run: {first_run}')
                    self.plotresults(first_run, run_epoch)
                    if(first_run):
                        self.inspecting = False
                    first_run = False
                    run_epoch = run_epoch + 1
                else:
                    plt.pause(1)                    
            except Exception as e:
                print(f'error {e} at {str(datetime.now())}')
                plt.pause(1)
            
plotter().plot()


#graveyard
      
            # for index in range(len(prediction_longitud[idx])):
            #     if index > trainingstops:
            #         # diff = np.absolute(labeldata_longitud[idx][index-trainingstops]-prediction_longitud[idx][index-trainingstops])
            #         # avrage_diff.append(diff)
            #         actual_change = labeldata_longitud[idx][index+trainingstops]/labeldata_longitud[idx][index-SettingsObject.lookToTheFuture+trainingstops]
            #         predicted_change = prediction_longitud[idx][index]/prediction_longitud[idx][index-SettingsObject.lookToTheFuture]
                    
            #         if(actual_change >= 1 and predicted_change >= 1):
            #             self.accuracy[idx]['pos_correct'] = self.accuracy[idx]['pos_correct'] + 1 
            #         elif(actual_change < 1 and predicted_change < 1):
            #             self.accuracy[idx]['neg_correct'] = self.accuracy[idx]['neg_correct'] + 1 
            #         elif(actual_change < 1 ):
            #             self.accuracy[idx]['neg_error'] = self.accuracy[idx]['neg_error'] + 1 
            #         elif(actual_change >= 1):
            #             self.accuracy[idx]['pos_error'] = self.accuracy[idx]['pos_error'] + 1 
                    
            #     else:
            #         continue
            
            # # print(f'stock: {idx}, correct pos {self.accuracy[idx]["pos_correct"]} neg {self.accuracy[idx]["neg_correct"]}  ') 
            # # print(f'stock: {idx}, error pos {self.accuracy[idx]["pos_error"]} neg {self.accuracy[idx]["neg_error"]}  ') 
            # totalerrors = (self.accuracy[idx]["neg_error"]+self.accuracy[idx]["pos_error"])
            # total_corrects = (self.accuracy[idx]["pos_correct"]+self.accuracy[idx]["neg_correct"])
            # all_preds = total_corrects + totalerrors
            # print(f'stock: {idx}, precition accyracy {(total_corrects*100)/all_preds}%') 
            # if not idx in self.Last_pred_first_index:
            #     self.Last_pred_first_index[idx] = []
            #     self.Last_pred_first_index[idx].append(50)
            
            
            # if self.Last_pred_first_index[idx][-1] != ((total_corrects*100)/all_preds) or make_this_round:
            #     make_this_round = True
            #     self.Last_pred_first_index[idx].append((total_corrects*100)/all_preds)
            #     # for index,value in enumerate(self.Last_pred_first_index[idx]):
            #     #     if not idx in avragepreds:
            #     #         avragepreds[idx] = []
            #     #     if index > avrageWindow:
            #     #         avrage = sum(avragepreds[idx][index-avrageWindow:index]) / avrageWindow
            #     #         avragepreds[idx].append(avrage)
                        
        #     plt.pause(0.1)
        # if not 99 in self.figs:
        #     self.figs[99]=plt.figure()
        # else:
        #     self.figs[99].clear()

        
        # avrage = sum(self.Last_pred_first_index)/len(self.Last_pred_first_index)  
        # self.axs[99]=self.figs[99].add_subplot(111)
        
        # #self.axs[idx].plot(training_longitud[idx], color = 'blue', linewidth=2 )
        # avrage = []
        # for index44, inex_graph in enumerate(self.Last_pred_first_index):

        #     self.axs[99].plot(self.Last_pred_first_index[inex_graph], linewidth=1)
        #     avrage.append(self.Last_pred_first_index[inex_graph][-1])
        
        # #self.avrage_pred.append(sum(avrage)/len(avrage))
        # self.axs[99].plot(avrage, linewidth=3)
        
        # self.figs[idx].show()
        # self.figs[99].show()





         # if not 'avrage' in self.figs:
        #     self.figs['avrage']=plt.figure(figsize=(width*px, height*px))
        # else:
        #     self.figs[idx].clear()
        # if (first_run):
            
        #     rowindex = int((totalgraphs+2)/sqrcount)*rowheight
        #     colindex = int((totalgraphs+2)%sqrcount)*colwidth
        #     # mngr = plt.get_current_fig_manager()äö
        #     # mngr.window.setGeometry(colindex,rowindex,6,5)
        #     backend = matplotlib.get_backend()
        #     if backend == 'TkAgg':
        #         self.figs[idx].canvas.manager.window.wm_geometry("+%d+%d" % (colindex,rowindex ))
        #     elif backend == 'WXAgg':
        #         self.figs[idx].canvas.manager.window.SetPosition((colindex, rowindex))
        #     else:
        #         # This works for QT and GTK
        #         # You can also use window.setGeometry
        #         self.figs[idx].canvas.manager.window.move(colindex, rowindex)
                


        #     self.cids[idx] = self.figs[idx].canvas.mpl_connect('resize_event', self.onclick)
        #     self.inspecting = False
        # #self.figs[idx].set_size_pi
        # self.axs[idx]=self.figs[idx].add_subplot(111)
        
        # #self.axs[idx].plot(training_longitud[idx], color = 'blue', linewidth=2 )
        
        
        


        # labellen = len(labeldata_longitud[idx])
        # predlen = len(prediction_longitud[idx])
        # trainlen = len(training_longitud[idx])
        # lookback = predlen

        # firsttrainingDay =  datetime.strptime(DataDateSpan[0], "%Y-%m-%d")
        # lasttrainday = datetime.strptime(PredDateSpan[-1], "%Y-%m-%d") +  timedelta(days=trainlen)
        
        # traindays = mdates.drange(firsttrainingDay,  lasttrainday, datetime.timedelta(days=1))

        # #self.figs[idx].gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        # #self.figs[idx].gca().xaxis.set_major_locator(mdates.DayLocator(interval=28))
        # lookbackmultiplier = 1
        
        # validSpace = np.linspace(int(trainlen), int(labellen-1), num=(labellen)-(trainlen))
        
        # PredictionSpace = np.linspace(int(labellen), int(labellen+(predlen-validSpace.size-1)), num=(predlen-validSpace.size)) 
            
        # trainspace = np.linspace(int(trainlen-(lookbackmultiplier*lookback)),int(trainlen-1), num=((trainlen)-(trainlen-(lookbackmultiplier*lookback))))
        # labelspace = np.linspace(int(labellen-(lookbackmultiplier*lookback)+SettingsObject.lookToTheFuture),int(labellen-1), num=(validSpace.size) )

        # predictionslice =  prediction_longitud[idx][validSpace.size:]
        # validslice = prediction_longitud[idx][0:validSpace.size]
        # labelslice = labeldata_longitud[idx][int(validSpace[0]):]
        # #trainingslice = training_longitud[idx][int(trainspace[0]):]


        # titel =str(tagetnames[idx])
        # self.axs[idx].set_title(titel)
        
        # if (run_epoch%2 == 0):

        #     self.axs[idx].plot(labelspace, labelslice, color = 'red', linewidth=1)
        #     #self.axs[idx].plot(trainspace, trainingslice, color = 'blue', linewidth=1)
        #     self.axs[idx].plot(PredictionSpace, predictionslice, color = 'green', linewidth=1)
        #     self.axs[idx].plot(validSpace, validslice, color = 'grey', linewidth=1)
        # else:
        #     self.axs[idx].plot(labeldata_longitud[idx], color = 'red', linewidth=1)
        #     self.axs[idx].plot(training_longitud[idx], color = 'blue', linewidth=1)
        #     self.axs[idx].plot(PredictionSpace, predictionslice, color = 'green', linewidth=1)
        #     self.axs[idx].plot(validSpace, validslice, color = 'grey', linewidth=1)
            
        
        # self.comps[idx] = []
        # self.accuracy[idx] = {'pos_correct': 0, 'neg_correct': 0, 'pos_error': 0, 'neg_error': 0, }


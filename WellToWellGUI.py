from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'width', '1600')
Config.set('graphics', 'height', '1200')
import kivy
kivy.require('1.11.1')
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
# noinspection ProblematicWhitespace
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty
from datetime import datetime
from pathlib import Path
import logging, os
from WellLit.WellLitGUI import WellLitWidget
from WellLit.Transfer import TError, TConfirm, TStatus
from WellToWell import WelltoWell

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    load_path = StringProperty('')


class WelltoWellWidget(WellLitWidget):
    """
    Loads csv files as directed by user to build well-to-well transfer protocols, and provides functionality
    for stepping through protocols using GUI buttons. Catches errors thrown by invalid user actions and displays error
    message in popups.
    """
    dest_plate = StringProperty()
    source_plate = StringProperty()
    current_tf_id = StringProperty()
    status = StringProperty()

    def __init__(self, **kwargs):
        super(WelltoWellWidget, self).__init__(**kwargs)
        cwd = os.getcwd()
        self.config_path = os.path.join(cwd, "wellLitConfig.json")
        self.wtw = WelltoWell(self.config_path)
        self.initialized = False
        self.dest_plate = ''
        self.source_plate = ''
        self.current_tf_id = ''
        self.status = 'Shortcuts: \n n: next transfer \n p: next plate \n q: quit program'
        self.load_path = self.wtw.load_path
        self.filename = ''

    def reset(self):
        self.status = 'Shortcuts: \n n: next transfer \n p: next plate \n q: quit program'
        self.dest_plate = ''
        self.source_plate = ''

    def quitConfirm(self):
        self.showPopup('Are you sure you want to exit?', 'Confirm exit', func=self.quit)

    def _on_keyboard_up(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'n':
            self.next()
        if keycode[1] == 'p':
            self.nextPlate(None)

    def load(self, filename):
        self.dismiss_popup()
        self.filename = filename
        if self.wtw.tp_present_bool():
            if not self.wtw.tp.protocolComplete():
                self.showPopup(TConfirm(
                    'Current protocol incomplete, loading a new protocol will abort the current one and skip remaining transfers. \n Are you sure you want to do this?'),
                               'Confirm protocol abort',
                               func=self.skipAndLoad)
            else:
                self.loadConfirm(filename)
        else:
            self.loadConfirm(filename)

    def skipAndLoad(self, filename):
        self.finishTransferConfirm(None)
        self.load(self.filename)

    def loadConfirm(self, filename):
        if filename:
            filename = filename[0]
        else:
            self.showPopup(TError('Invalid target to load'), 'Unable to load file')

        if os.path.isfile(str(filename)):
            try:
                logging.info('User selected file %s to load' % filename)
                self.wtw.loadCsv(filename)
            except TError as err:
                self.showPopup(err, 'Load Failed')
            except TConfirm as conf:
                self.showPopup(conf, 'Load Successful')
                if not self.initialized:
                    self.reset_plates()
                    self.initialized = True
                self.wtw.tp.id_type = ''
                self.updateLights()
                self.dest_plate = self.wtw.dest_plate
                self.updateLabels()
                self.next()


    def updateLabels(self):
        self.source_plate = self.wtw.tp.current_plate_name

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup, load_path=self.load_path)
        self._popup = Popup(title='Load File', content=content)
        self._popup.size_hint = (0.3, 0.375)
        self._popup.pos_hint = {'center_x': 0.5, 'y': 0}
        self._popup.open()

    def updateLights(self):
        '''
        At each step:
        dest_wells: completed -> filled, uncompleted -> empty
        source_wells: completed -> empty, uncompletled -> full
        color current target wells, and black out wells not involved in transfer
        '''
        # self.ids.source_plate.pl.blackoutWells()
        # self.ids.dest_plate.pl.blackoutWells()

        self.ids.source_plate.pl.emptyWells()
        self.ids.dest_plate.pl.emptyWells()

        if self.wtw.tp_present_bool():

            current_transfers = self.wtw.tp.transfers_by_plate[self.wtw.tp.current_plate_name]

            # For transfer that is complete, color source well empty and dest well as full
            for tf_id in self.wtw.tp.lists['completed']:
                self.ids.dest_plate.pl.markFilled(self.wtw.tp.transfers[tf_id]['dest_well'])
                if tf_id in current_transfers:
                    self.ids.source_plate.pl.markEmpty(self.wtw.tp.transfers[tf_id]['source_well'])

            # For transfer that is uncomplete, mark source well as full, dest well as empty
            for tf_id in list(set(current_transfers) & set(self.wtw.tp.lists['uncompleted'])):
                self.ids.source_plate.pl.markFilled(self.wtw.tp.transfers[tf_id]['source_well'])
                self.ids.dest_plate.pl.markEmpty(self.wtw.tp.transfers[tf_id]['dest_well'])

            # skipped wells in source are full, and empty in dest
            for tf_id in list(set(current_transfers) & set(self.wtw.tp.lists['skipped'])):
                self.ids.source_plate.pl.markFilled(self.wtw.tp.transfers[tf_id]['source_well'])
                self.ids.dest_plate.pl.markEmpty(self.wtw.tp.transfers[tf_id]['dest_well'])

            # Mark current targets
            if self.wtw.tp.transfers[self.wtw.tp.current_uid].status == TStatus.started:
                self.ids.source_plate.pl.markTarget(self.wtw.tp.transfers[self.wtw.tp.current_uid]['source_well'])
                self.ids.dest_plate.pl.markTarget(self.wtw.tp.transfers[self.wtw.tp.current_uid]['dest_well'])

            self.current_tf_id = self.wtw.tp.tf_id()

            self.ids.source_plate.pl.show()
            self.ids.dest_plate.pl.show()

    def complete(self):
        if self.canUpdate():
            self.transfers[self.current_uid].updateStatus(TStatus.completed)
            self.log('transfer complete: %s' % self.tf_id())


    def start(self):
        if self.canUpdate():
            self.transfers[self.current_uid].updateStatus(TStatus.started)
            self.log('transfer started: %s' % self.tf_id())

    def next(self):
        try:
            self.wtw.next()
            self.status = self.wtw.tp.msg
            self.updateLights()
        except TError as err:
            self.showPopup(err, 'Unable to complete transfer')
            self.status = err.__str__()
        except TConfirm as conf:
            self.showPopup(conf, 'Plate complete', func=self.nextPlate)
            self.status = conf.__str__()
        if self.wtw.tp_present_bool():
            self.wtw.writeTransferRecordFiles(None)

    def skip(self):
        try:
            self.wtw.skip()
            self.status = self.wtw.tp.msg
            self.updateLights()
        except TError as err:
            self.showPopup(err, 'Unable to skip transfer')
            self.status = err.__str__()
        except TConfirm as conf:
            self.showPopup(conf, '')
            self.status = conf.__str__()
        if self.wtw.tp_present_bool():
            self.wtw.writeTransferRecordFiles(None)

    def failed(self):
        try:
            self.wtw.failed()
            self.status = self.wtw.tp.msg
            self.updateLights()
        except TError as err:
            self.showPopup(err, 'Unable to abort transfer')
            self.status = err.__str__()
        except TConfirm as conf:
            self.showPopup(conf, '')
            self.status = conf.__str__()
        if self.wtw.tp_present_bool():
            self.wtw.writeTransferRecordFiles(None)

    def undo(self):
        try:
            self.wtw.undo()
            self.status = self.wtw.tp.msg
            self.updateLights()
        except TError as err:
            self.showPopup(err, 'Unable to undo transfer')
            self.status = err.__str__()
        except TConfirm as conf:
            self.showPopup(conf, '')
            self.status = conf.__str__()
        if self.wtw.tp_present_bool():
            self.wtw.writeTransferRecordFiles(None)

    def nextPlate(self, _):
        self.status = ''
        try:
            self.wtw.nextPlate()
        except TError as err:
            if self.wtw.tp_present_bool():
                self.showPopup(err, 'Confirm skip remaining', func=self.nextPlateOverride)
            else:
                self.showPopup(err, 'Unable to complete plate')
            self.status = err.__str__()
        except TConfirm as conf:
            self.nextPlateConfirm(None)
            self.wtw.writeTransferRecordFiles(None)
            self.updateLabels()
            self.updateLights()
            self.next()

    def nextPlateConfirm(self, _):
        try:
            self.wtw.nextPlateConfirm()
            self.status = self.wtw.tp.msg
            self.updateLights()
        except TError as err:
            self.showPopup(err, 'Cannot load next plate')
            self.status = err.__str__()
        except TConfirm as conf:
            self.showPopup(conf, 'Load next plate')
            self.updateLabels()
            self.updateLights()
        if self.wtw.tp_present_bool():
            self.wtw.writeTransferRecordFiles(None)

    def nextPlateOverride(self, _):
        try:
            self.wtw.nextPlateOverride()
            self.status = self.wtw.tp.msg
            self.updateLights()
        except TError as err:
            self.showPopup(err, 'Cannot override plate skip')
            self.status = err.__str__()
            self.updateLights()
        except TConfirm as conf:
            self.showPopup(conf, 'Plate skipped')
            self.status = conf.__str__()
            self.wtw.writeTransferRecordFiles(None)
            self.updateLabels()
            self.updateLights()
            self.next()
        if self.wtw.tp_present_bool():
            self.wtw.writeTransferRecordFiles(None)

    def finishTransfer(self):
        if self.initialized:
            if not self.wtw.tp.protocolComplete():
                self.showPopup(TConfirm(
                    'Are you sure you wish to finish this transfer protocol? \n All remaining transfers will be skipped'),
                               'Confirm transfer abort',
                               func=self.finishTransferConfirm)
                if self.wtw.tp_present_bool():
                    self.wtw.writeTransferRecordFiles(None)
            else:
                self.finishTransferConfirm(None)


    def finishTransferConfirm(self, _):
        try:
            # Reset lighting on both WellLit plates

            self.ids.source_plate.pl.blackoutWells()
            self.ids.dest_plate.pl.blackoutWells()
            self.ids.source_plate.pl.show()
            self.ids.dest_plate.pl.show()

            # write transfer record files
            self.wtw.writeTransferRecordFiles(None)
            self.showPopup(TConfirm('Record file generated, press \'q\' to quit or load a new transfer'),
                           'Transfers complete')

            # reset internal state and clear messages
            self.wtw.reset()
            self.reset()
            self.updateLights()
        except TError as err:
            self.showPopup(err, 'Error aborting transfer')
            self.status = err.__str__()
        if self.wtw.tp_present_bool():
            self.wtw.writeTransferRecordFiles(None)

    def setSquareMarker(self):
        """
        Change shape of source well plate
        """
        if self.initialized:
            self.ids.source_plate.pl.setMarker('square')

    def setCircleMarker(self):
        """
        Change shape of source well plate
        """
        if self.initialized:
            self.ids.source_plate.pl.setMarker('circle')


class WellToWellApp(App):
    kv_file='OrderedLayout.kv'
    def build(self):
        return WelltoWellWidget()


if __name__ == '__main__':
    cwd = os.getcwd()
    logdir = os.getcwd() + '/logs/'
    logfile = 'WelltoWell_Logfile_' + datetime.utcnow().strftime('%Y_%m_%d') + '.txt'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] - %(message)s',
        filename=Path(logdir + logfile))  # pass explicit filename here
    logger = logging.getLogger()  # get the root loggers
    logging.info('Session started')

   # Window.size = (1600, 1200)
   # Window.fullscreen = True
    WellToWellApp().run()
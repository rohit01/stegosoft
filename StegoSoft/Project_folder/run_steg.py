#!/usr/bin/python -d
#
# StegoSoft is a software which implements steganography using
# audio files. This software can hide message files inside a
# audio file by using the Least Significant Bit Algorithm.
# 
# Developed by:
# Rohit Gupta
# E-mail: rohit.kgec@gmail.com
# 
# as a final year project,
# B.Tech IT,
# Kalyani Government Engineering College,
# Kalyani, Nadia (W.B), India
#
# License: GNU GPL v2
#


import sys
import os
import shutil
from PyQt4 import QtCore, QtGui
from stegosoft_ui import Ui_stegosoft_gui
from cryptography import cryptography

class MyForm(QtGui.QMainWindow):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.flag = QtCore.Qt.WindowFlags( 3 )
    QtGui.QWidget.setWindowFlags(self, self.flag )
    self.ui = Ui_stegosoft_gui()
    self.ui.setupUi(self)
    self.crypto = cryptography( self )
    self.ui.tableWidget_for_hide_message_files.setShowGrid( False )
    working_directory = os.path.abspath("./")
    help_file_url = "file://" + "%20".join(working_directory.split(" ")) + "/documentation/documentation.html"
    self.ui.webView_help.load( QtCore.QUrl( help_file_url ) )
    QtCore.QObject.connect(self.ui.pushButton_browse_master_file, QtCore.SIGNAL("clicked()"), self.select_file_browse_master )
    QtCore.QObject.connect(self.ui.pushButton_browse_carrier_file, QtCore.SIGNAL("clicked()"), self.select_file_browse_carrier )
    QtCore.QObject.connect(self.ui.pushButton_add_message_file, QtCore.SIGNAL("clicked()"), self.select_file_add_message_file )
    QtCore.QObject.connect(self.ui.pushButton_remove_message_file, QtCore.SIGNAL("clicked()"), self.remove_message_file )
    QtCore.QObject.connect(self.ui.pushButton_hide_submit, QtCore.SIGNAL("clicked()"), self.hide_submit )
    QtCore.QObject.connect(self.ui.pushButton_unhide_submit, QtCore.SIGNAL("clicked()"), self.unhide_submit )
    QtCore.QObject.connect(self.ui.pushButton_show_message_files, QtCore.SIGNAL("clicked()"), self.extract_header )
    self.ui.checkBox_use_password.clicked.connect (self.is_password_needed)
    self.hide_password_character_status = "No"
    self.hide_confirm_password_character_status = "No"
    self.unhide_password_character_status = "No"
    QtCore.QObject.connect(self.ui.lineEdit_hide_password, QtCore.SIGNAL("selectionChanged()"), self.lineEdit_hide_clear_and_set_password_character )
    QtCore.QObject.connect(self.ui.lineEdit_hide_confirm_password, QtCore.SIGNAL("selectionChanged()"), self.lineEdit_hide_confirm_clear_and_set_password_character )
    QtCore.QObject.connect(self.ui.lineEdit_unhide_password, QtCore.SIGNAL("selectionChanged()"), self.lineEdit_unhide_clear_and_set_password_character )


  def lineEdit_hide_clear_and_set_password_character(self):
    if self.hide_password_character_status == "No":
      self.ui.lineEdit_hide_password.clear()
      self.ui.lineEdit_hide_password.setEchoMode(2)
      self.hide_password_character_status = "Yes"

  def lineEdit_hide_confirm_clear_and_set_password_character(self):
    if self.hide_confirm_password_character_status == "No":
      self.ui.lineEdit_hide_confirm_password.clear()
      self.ui.lineEdit_hide_confirm_password.setEchoMode(2)
      self.hide_confirm_password_character_status = "Yes"

  def lineEdit_unhide_clear_and_set_password_character(self):
    if self.unhide_password_character_status == "No":
      self.ui.lineEdit_unhide_password.clear()
      self.ui.lineEdit_unhide_password.setEchoMode(2)
      self.unhide_password_character_status = "Yes"

  def select_file_browse_master(self):
    filename=QtGui.QFileDialog.getOpenFileName( None, "Open a Master File", "/home", "Wav Format(*.wav)")
    if filename != "":
      self.ui.label_master_file_path.setText( filename )
      self.ui.label_master_file_size.setText( self.get_filesize(filename) )
      self.ui.label_master_file_path.setAlignment( self.ui.label_master_file_size.alignment() )

  def select_file_browse_carrier(self):
    filename=QtGui.QFileDialog.getOpenFileName( None, "Open a Carrier File", "/home", "Wav Format(*.wav)")
    if filename != "":
      self.ui.label_carrier_file_path.setText( filename )
      self.ui.label_carrier_file_size.setText( self.get_filesize(filename) )
      self.ui.label_carrier_file_path.setAlignment( self.ui.label_master_file_size.alignment() )

  def select_file_add_message_file(self):
    new_file=QtGui.QFileDialog.getOpenFileName( None, "Open a Message File", "/home", "All Files(*)")
    if new_file != "":
      no_of_rows = self.ui.tableWidget_for_hide_message_files.rowCount()
      i = 0
      self.message_filenames = []
      while i < no_of_rows:
        ith_file = self.ui.tableWidget_for_hide_message_files.takeItem( i, 3).data(0).toString()
        self.ui.tableWidget_for_hide_message_files.setItem( i, 3, QtGui.QTableWidgetItem( ith_file ))
        if ith_file == new_file:
          QtGui.QMessageBox.information(self, "Duplicate File!", "You have already selected the file concerned.\nPlease select a different file to hide.")
          return 1
        self.message_filenames.append( str(ith_file.split("/")[-1]) )
        i = i+1
      new_filename = self.resolve_duplicate_filenames( new_file.split("/")[-1], self.message_filenames )
      if new_filename != None:
        accept = QtGui.QMessageBox.warning(self, "File will be renamed when added!", str("The file named '" + new_file.split("/")[-1] + "' already exists.\nIf added this file will be renamed to '" + new_filename + "' or similar.\nAre you sure you want to do this?"), "Yes", "No" )
        if accept == 1:
          return 1
      self.ui.tableWidget_for_hide_message_files.insertRow( no_of_rows )
      self.ui.tableWidget_for_hide_message_files.setItem( no_of_rows, 0, QtGui.QTableWidgetItem( new_file.split("/")[-1] ))
      self.ui.tableWidget_for_hide_message_files.setItem( no_of_rows, 1, QtGui.QTableWidgetItem( self.get_filesize(new_file) ))
      if self.ui.checkBox_use_password.isChecked() == True:
        self.ui.tableWidget_for_hide_message_files.setItem( no_of_rows, 2, QtGui.QTableWidgetItem( "Yes" ))
      else:
        self.ui.tableWidget_for_hide_message_files.setItem( no_of_rows, 2, QtGui.QTableWidgetItem( "No" ))
      self.ui.tableWidget_for_hide_message_files.setItem( no_of_rows, 3, QtGui.QTableWidgetItem( new_file ))

  def remove_message_file(self):
    row_number = self.ui.tableWidget_for_hide_message_files.currentRow()
    self.ui.tableWidget_for_hide_message_files.removeRow( row_number )

  def is_password_needed(self):
    no_of_rows = self.ui.tableWidget_for_hide_message_files.rowCount()
    if self.ui.checkBox_use_password.isChecked() == True:
      i = 0
      while i < no_of_rows:
        self.ui.tableWidget_for_hide_message_files.setItem( i, 2, QtGui.QTableWidgetItem( "Yes" ))
        i = i+1
      self.ui.lineEdit_hide_password.setMaxLength(28)
      self.ui.lineEdit_hide_confirm_password.setMaxLength(28)
    else:
      i = 0
      while i < no_of_rows:
        self.ui.tableWidget_for_hide_message_files.setItem( i, 2, QtGui.QTableWidgetItem( "No" ))
        i = i+1
      self.ui.lineEdit_hide_password.setMaxLength(28)
      self.ui.lineEdit_hide_confirm_password.setMaxLength(28)

  def get_filesize( self, filename ):
    filesize = os.path.getsize( filename )
    if filesize < 1024:
      return ' '.join( [ str(filesize), "B"] )
    elif 1024 <= filesize < 1024**2:
      filesize = int( round( filesize/1024.0**1 ))
      return ' '.join( [ str(filesize), "KB"] )
    elif 1024**2 <= filesize < 1024**3:
      filesize = int( round( filesize/1024.0**2 ))
      return ' '.join( [ str(filesize), "MB"] )
    elif filesize >= 1024**3:
      filesize = int( round( filesize/1024.0**3 ))
      return ' '.join( [ str(filesize), "GB"] )

  def resolve_duplicate_filenames( self, input_filename, message_filenames, no_of_occurrence=0 ):
    resolved_filename = None
    input_filename = str(input_filename)
    if input_filename in message_filenames:
      if no_of_occurrence > 0:
        i = 0
        for item in message_filenames:
          if item == input_filename:
            i = i+1
        if i <= no_of_occurrence:
          return None
      i = 2
      resolved_filename = input_filename
      while resolved_filename in message_filenames:
        if ".".join( input_filename.split('.')[:-1] ) != "":
          resolved_filename = ".".join( input_filename.split('.')[:-1] ) + '_' + str(i) + '.' + input_filename.split('.')[-1]
        else:
          resolved_filename = str(resolved_filename + '_' + str(i))
        i = i+1
    return resolved_filename

  def hide_resolve_duplicate_filenames( self ):
    no_of_rows = self.ui.tableWidget_for_hide_message_files.rowCount()
    i = 0
    self.message_filenames = []
    message_filenames = []
    while i < no_of_rows:
      ith_file = self.ui.tableWidget_for_hide_message_files.takeItem( i, 3).data(0).toString()
      self.ui.tableWidget_for_hide_message_files.setItem( i, 3, QtGui.QTableWidgetItem( ith_file ))
      self.message_filenames.append( str(ith_file))
      message_filenames.append( str(ith_file).split('/')[-1] )
      i = i+1
    file_dict = {}
    i = 0
    while i < no_of_rows:
      new_filename = self.resolve_duplicate_filenames( self.message_filenames[i].split('/')[-1] , message_filenames, 1 )
      if new_filename != None:
        if self.message_filenames[i].split('/')[-1] in file_dict:
          temp_filename = "./temp/resolve/" + new_filename
          message_filenames.append( new_filename )
          shutil.copy2( self.message_filenames[i], temp_filename)
          self.message_filenames[i] = temp_filename
        else:
          file_dict[ self.message_filenames[i].split('/')[-1] ] = "resolve"
      i = i+1
    return 0

  def hide_submit(self):
    master_filename = str( self.ui.label_master_file_path.text() )
    no_of_message_files = self.ui.tableWidget_for_hide_message_files.rowCount()
    if master_filename == "No File Selected":
      QtGui.QMessageBox.information(self, "Please Select a Master File!", "No Master File selected.\nPlease Select a Master file to continue.")
      return 1
    if no_of_message_files == 0:
      QtGui.QMessageBox.information(self, "Please Add Some Message Files!", "You have not added a single message file.\nPlease add one or more message files to continue.")
      return 1
    if (self.ui.checkBox_use_password.isChecked() == True) and \
       ((self.hide_password_character_status == "No") or (self.hide_confirm_password_character_status == "No")):
      QtGui.QMessageBox.information(self, "Please Enter a Password!", "Password must be entered if used for security.\nPlease Enter Password to continue.")
      return 1
    elif (self.ui.checkBox_use_password.isChecked() == True) and \
         (self.ui.lineEdit_hide_password.text() == "" and self.ui.lineEdit_hide_confirm_password.text() == ""):
      print self.ui.lineEdit_hide_password.text()
      print self.ui.lineEdit_hide_confirm_password.text()
      QtGui.QMessageBox.information(self, "Null Password Entered!", "The password cannot be blank.\nPlease enter passwords correctly to continue.")
      return 1
    elif (self.ui.checkBox_use_password.isChecked() == True) and \
         ((self.ui.lineEdit_hide_password.text() != self.ui.lineEdit_hide_confirm_password.text())):
      print self.ui.lineEdit_hide_password.text()
      print self.ui.lineEdit_hide_confirm_password.text()
      QtGui.QMessageBox.information(self, "Passwords do not Match!", "The passwords in both the boxes must be the same.\nPlease enter passwords correctly to continue.")
      return 1

    output_filename = QtGui.QFileDialog.getSaveFileName( None, "Save the Carrier file as.." , "master.wav", "Wav Format(*.wav)")
    if output_filename != "":
      no_of_rows = self.ui.tableWidget_for_hide_message_files.rowCount()
      self.hide_resolve_duplicate_filenames()
      run_hide_program = [ './hide.out' ]
      run_hide_program.append( ''.join(['"', str(master_filename), '"']) )
      run_hide_program.append( ''.join(['"', str(output_filename), '"']) )
      run_hide_program.append( ''.join(['"', str(no_of_rows), '"']) )
      if self.ui.checkBox_use_password.isChecked() == False:
        run_hide_program.append( ''.join(['"', str(0), '"']) )
        run_hide_program.append( ''.join(['"', str(0), '"']) )
        i = 0
        while i < no_of_rows:
          run_hide_program.append( ''.join(['"', str( os.path.getsize(self.message_filenames[i]) ), '"']) )
          run_hide_program.append( ''.join(['"', str( str( self.message_filenames[i]).split('/')[-1].__len__() ), '"']) )
          run_hide_program.append( ''.join(['"', str( 0 ), '"']) )
          run_hide_program.append( ''.join(['"', str( self.message_filenames[i] ), '"']) )
          i = i + 1
      else:
        run_hide_program.append( ''.join(['"', str(1), '"']) )
        self.hide_password = str( self.crypto.encrypt( str(self.ui.lineEdit_hide_password.text()), str(self.ui.lineEdit_hide_password.text()) ) )
        print self.hide_password
        run_hide_program.append( ''.join(['"', self.hide_password , '"']) )
        i = 0
        while i < no_of_rows:
          encrypted_filename = "./temp/" + str( self.message_filenames[i]).split('/')[-1]
          self.crypto.encrypt_file( self.message_filenames[i], encrypted_filename, self.hide_password)

          run_hide_program.append( ''.join(['"', str( os.path.getsize( encrypted_filename ) ), '"']) )
          run_hide_program.append( ''.join(['"', str( str( self.message_filenames[i]).split('/')[-1].__len__() ), '"']) )
          run_hide_program.append( ''.join(['"', str( 1 ), '"']) )
          run_hide_program.append( ''.join(['"', encrypted_filename, '"']) )
          i = i + 1 
      print ' '.join( run_hide_program )
      success = os.system( ' '.join( run_hide_program ) )
      for i in os.listdir( "./temp/resolve/" ):
        try:
          os.remove("./temp/resolve/" + i)
        except:
          pass
      for i in os.listdir( "./temp/" ):
        try:
          os.remove("./temp/" + i)
        except:
          pass
      if int(success) == 0:
        QtGui.QMessageBox.information(self, "File Successfully Created!", "Hide Operation Completed Successfully.\nCongratulations!!.")
        return 0
      else:
        QtGui.QMessageBox.information(self, "Unexpected error!", "Sorry the hide operation failed.\nPlease report your problems to developers by e-mail.")
        return 1


  def unhide_submit(self):
    self.carrier_filename = str( self.ui.label_carrier_file_path.text() )
    if self.carrier_filename == "No File Selected":
      QtGui.QMessageBox.information(self, "Please Select a Carrier File!", "No Carrier File selected.\nPlease Select a Carrier file to continue.")
      return 1
    if self.extract_header() == 1:
      return 1

    self.output_folder=QtGui.QFileDialog.getExistingDirectory( None, "Select where to save the files" , "")
    if self.output_folder != "":
      self.carrier_filename = self.ui.label_carrier_file_path.text()
      run_unhide_program = [ './unhide.out' ]
      run_unhide_program.append( ''.join(['"', str(self.carrier_filename), '"']) )
      if int(self.header[3]) != 0:
        run_unhide_program.append( ''.join(['"', "./temp/" , '"']) )
        if self.unhide_password_character_status == "Yes":
          self.unhide_password = str( self.crypto.encrypt( str(self.ui.lineEdit_unhide_password.text()) , str(self.ui.lineEdit_unhide_password.text())) )
          run_unhide_program.append( ''.join(['"', self.unhide_password, '"']) )
        print ' '.join( run_unhide_program )
        success = os.system( ' '.join( run_unhide_program ) )
        if int(success) == 0:
          no_of_rows = self.ui.tableWidget_for_unhide_message_files.rowCount()
          i = 0
          self.message_filenames = []
          while i < no_of_rows:
            ith_file = self.ui.tableWidget_for_unhide_message_files.takeItem( i, 0).data(0).toString()
            self.ui.tableWidget_for_unhide_message_files.setItem( i, 0, QtGui.QTableWidgetItem( ith_file ))
            self.message_filenames.append( str(ith_file) )
            self.unhide_password = str( self.crypto.encrypt( str(self.ui.lineEdit_unhide_password.text()) , str(self.ui.lineEdit_unhide_password.text())) )
            self.crypto.decrypt_file( str("./temp/" + ith_file), str(str(self.output_folder) + "/" + ith_file), self.unhide_password )
            i = i + 1
      else:
        run_unhide_program.append( ''.join(['"', ''.join([str(self.output_folder), "/"]), '"']) )
        success = os.system( ' '.join( run_unhide_program ) )
      print ' '.join( run_unhide_program )
      for i in os.listdir( "./temp/resolve/" ):
        try:
          os.remove("./temp/resolve/" + i)
        except:
          pass
      for i in os.listdir( "./temp/" ):
        try:
          os.remove("./temp/" + i)
        except:
          pass
      if int(success) == 0:
        QtGui.QMessageBox.information(self, "File(s) Successfully Extracted!", "Unhide Operation Completed Successfully.\nCongratulations!!.")
        return 0
      else:
        QtGui.QMessageBox.information(self, "Error!", "Sorry the unhide operation failed.\nPlease ensure that you have entered the password correctly.\nIf problems still exists, report to developers by e-mail.")
        return 1

  def extract_header(self):
    self.carrier_filename = str( self.ui.label_carrier_file_path.text() )
    if self.carrier_filename == "No File Selected":
      QtGui.QMessageBox.information(self, "Please Select a Carrier File!", "No Carrier File selected.\nPlease Select a Carrier file to continue.")
      return 1
### extract the header ###
    run_unhide_program = [ './extract.out' ]
    run_unhide_program.append( ''.join(['"', str(self.carrier_filename), '"']) )
    success = os.system( ' '.join( run_unhide_program ) )
    self.header = []
    for line in open("./HeaderInfo.h", 'r'):
      self.header.append( str(line).split('\n')[0] )
    try:
      os.remove("./HeaderInfo.h")
    except:
      pass
### extracted ###
    if self.unhide_password_character_status == "Yes" and str(self.ui.lineEdit_unhide_password.text()) != "":
      self.unhide_password = str( self.crypto.encrypt( str(self.ui.lineEdit_unhide_password.text()) , str(self.ui.lineEdit_unhide_password.text())) )
      if int(self.header[3]) == 0:
        QtGui.QMessageBox.information(self, "Incorrect Password!", "Please check the password you have entered.")
        return 1
      else:
        if self.unhide_password != self.header[6]:
          QtGui.QMessageBox.information(self, "Incorrect Password!", "Please check the password you have entered.")
          return 1
      i = 0
      no_of_rows = self.ui.tableWidget_for_unhide_message_files.rowCount()
      for filename in self.header[10::4]:
        if i >= no_of_rows:
          self.ui.tableWidget_for_unhide_message_files.insertRow( i )
        self.ui.tableWidget_for_unhide_message_files.setItem( i, 0, QtGui.QTableWidgetItem( filename ))
        i = i+1
      i = 0
      for filesize in self.header[7::4]:
        self.ui.tableWidget_for_unhide_message_files.setItem( i, 1, QtGui.QTableWidgetItem( filesize ))
        i = i+1
      i = 0
      for encryption in self.header[9::4]:
        if int(encryption) != 0:
          self.ui.tableWidget_for_unhide_message_files.setItem( i, 2, QtGui.QTableWidgetItem( "Yes" ))
        else:
          self.ui.tableWidget_for_unhide_message_files.setItem( i, 2, QtGui.QTableWidgetItem( "No" ))
        i = i+1
      row_number = i
      while i < no_of_rows:
        self.ui.tableWidget_for_unhide_message_files.removeRow( row_number )
        i = i+1
    elif int(self.header[3]) != 0:
      QtGui.QMessageBox.information(self, "Incorrect Password!", "Please check the password you have entered.")
      return 1
    else:
      i = 0
      no_of_rows = self.ui.tableWidget_for_unhide_message_files.rowCount()
      for filename in self.header[8::4]:
        if i >= no_of_rows:
          self.ui.tableWidget_for_unhide_message_files.insertRow( i )
        self.ui.tableWidget_for_unhide_message_files.setItem( i, 0, QtGui.QTableWidgetItem( filename ))
        i = i+1
      i = 0
      for filesize in self.header[5::4]:
        self.ui.tableWidget_for_unhide_message_files.setItem( i, 1, QtGui.QTableWidgetItem( filesize ))
        i = i+1
      i = 0
      for encryption in self.header[7::4]:
        if int(encryption) != 0:
          self.ui.tableWidget_for_unhide_message_files.setItem( i, 2, QtGui.QTableWidgetItem( "Yes" ))
        else:
          self.ui.tableWidget_for_unhide_message_files.setItem( i, 2, QtGui.QTableWidgetItem( "No" ))
        i = i+1
      row_number = i
      while i < no_of_rows:
        self.ui.tableWidget_for_unhide_message_files.removeRow( row_number )
        i = i+1
    print self.header


if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = MyForm()
  myapp.show()
  sys.exit(app.exec_())


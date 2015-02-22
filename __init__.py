#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------------
# Estimator: calculate space occupied by files presented in script
#
# Andrew Savchenko © 2014
# art@artaman.net
#
# splitter() © tixxit
#
# Attribution 4.0 International (CC BY 4.0)
# http://creativecommons.oseqMatch/licenses/by/4.0/
#
# Developed on OSX and RHEL, should work on random *nix system
# --------------------------------------------------------------
__version__ = "0.0.2"
__release__ = True

import nuke
import nukescripts
import os, sys
import threading
import random
estimator_path = os.getenv("HOME") + "/.nuke/estimator"
sys.path.append(estimator_path)
from pyseq import *
from filesize import size as sconvert

if nuke.GUI is True:
    class estimatorPanel(nukescripts.PythonPanel):

        def __init__(self):
            nukescripts.PythonPanel.__init__(
                self,
                'Estimator',
                'uk.co.thefoundry.estimatorPanel')
            self.runBtn = nuke.PyScript_Knob('Run')
            self.printBroken = nuke.Boolean_Knob('Output missing sequences')
            self.precisionValue = nuke.Int_Knob('Frames to calculate: ')
            self.divider = nuke.Text_Knob('')

            self.addKnob(self.precisionValue)
            self.addKnob(self.runBtn)
            self.addKnob(self.divider)
            self.addKnob(self.printBroken)

            self.precisionValue.setValue(10)

            global DEV
            DEV = 0

        def evaluate_script(self, checker=0):

            files_to_check = {}
            readTypes = ('Read', 'ReadGeo2')

            for node in nuke.allNodes():
                if node.knob('gizmo_file') is not None or node.Class() == "Group":
                    for subNode in nuke.toNode(node.name()).nodes():
                        if subNode.Class() in readTypes:
                            file_path = subNode.knob('file').value()
                            first = len(str(subNode.knob('first').value()))
                            last = len(str(subNode.knob('last').value()))
                            if file_path != "":
                                files_to_check.update({file_path:[first, last]})
                else:
                    if node.Class() in readTypes:
                        file_path = node.knob('file').value()
                        if file_path != "":
                            first = node.knob('first').value()
                            last = node.knob('last').value()
                            files_to_check.update({file_path:[first, last]})

            print "\n~ There are " + str(len(files_to_check)) + " sequences in this script.\n"

            total_size = 0
            seq_errors = 0
            seq_suspicious = 0
            for sequence, metadata in files_to_check.iteritems():
                    if DEV > 0:
                        print "* Sequence: " + sequence
                        print "range: " + str(metadata)
                    seq_padding = str(sequence.split(".")[:1][0]).split("/")[-1]
                    if len(seq_padding.split("#")) > 1:
                        seq_numbering = "%0" + str(seq_padding.count("#")) + "d"
                    elif len(seq_padding.split("%")) > 1:
                        seq_numbering = "%" + seq_padding.split("%")[-1]
                    else:
                        seq_numbering = None
                    seq_name_full = sequence + " " + str(metadata[0]) + "-" + str(metadata[1])
                    seq_object = uncompress(seq_name_full, format="%h%p%t %r")
                    seq_folder = "/".join(sequence.split("/")[:-1])
                    seq_niceName = sequence.split("/")[-1]
                    seq_size = 0
                    if DEV > 0:
                        print "seq_numbering: " + str(seq_numbering)
                        print "seq_name_full: " + seq_name_full
                        print "seq_object: " + str(seq_object)
                        print "seq_folder: " + seq_folder
                        print "seq_niceName: " + seq_niceName + "\n"
                    def splitter(a, n):
                        k, m = len(a) / n, len(a) % n
                        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))
                    if seq_object:
                            if metadata[1] - metadata[0] > 300:
                                seq_suspicious += 1
                            if len(seq_object.frames()) <= self.precisionValue.value():
                                for frame in seq_object.frames():
                                    if seq_numbering is not None:
                                        frame = str(frame).zfill(int(seq_numbering[2]))
                                        seq_frame = seq_object.format('%h') + frame + seq_object.format('%t')
                                        seq_frame_path = os.path.join(seq_folder, seq_frame)
                                    if DEV > 0:
                                        print ".: " + seq_frame_path
                                    if os.path.isfile(seq_frame_path) is True:
                                        seq_size += abs(os.path.getsize(seq_frame_path))
                                    else:
                                        if DEV > 0:
                                            print "\n! something wrong with " + seq_frame_path + "\n"
                            else:
                                approx_size = 0
                                split = list(splitter(seq_object.frames(), self.precisionValue.value()))
                                for x in split:
                                    frame = str(x[0]).zfill(int(seq_numbering[2]))
                                    seq_frame = seq_object.format('%h') + frame + seq_object.format('%t')
                                    seq_frame_path = os.path.join(seq_folder, seq_frame)
                                    print seq_frame_path
                                    if os.path.isfile(seq_frame_path) is True:
                                        approx_size += abs(os.path.getsize(seq_frame_path))
                                    else:
                                        if DEV > 0:
                                            print "\n! something wrong with " + seq_frame_path + "\n"
                                approx_size = approx_size / self.precisionValue.value() * metadata[1]
                                seq_size += approx_size
                    else:
                        if DEV > 0:
                            print ".: " + sequence
                        if os.path.isfile(sequence) is True:
                            seq_size += abs(os.path.getsize(sequence))

                    files_to_check[sequence].append(seq_size)
                    if checker > 0:
                        if seq_size > 0:
                            print "* " + seq_niceName + " .. " + sconvert(seq_size)
                        else:
                            seq_errors += 1
                            print "* " + seq_niceName + " .. " + sconvert(seq_size)
                    total_size += seq_size

            print "\n~ Total size: " + sconvert(total_size)
            if seq_suspicious == 1:
                print "~ There is " + str(seq_suspicious) + " suspiciously big sequence"
            elif seq_suspicious > 1:
                print "~ There are " + str(seq_suspicious) + " suspiciously big sequences"
            if seq_errors == 1:
                print "! There is " + str(seq_errors) + " read node with error"
            elif seq_errors > 1:
                print "! There are " + str(seq_errors) + " read nodes with errors"

        def knobChanged(self, knob):
            if knob is self.runBtn:
                threading.Thread(target=self.evaluate_script, args=(1,)).start()
            else:
                pass

    def addPanel():
        return estimatorPanel().addToPane()

if nuke.GUI is True:
    menu = nuke.menu("Pane")
    menu.addCommand("Estimator", addPanel)
    nukescripts.registerPanel(
        "uk.co.thefoundry.estimatorPanel", addPanel)
else:
    print "\n! Nuke is running in non-gui mode"
# -*- coding: utf-8 -*-
# --------------------------------------------------------------
# Estimator: calculate space occupied by files presented in script
#
# Andrew Savchenko © 2015
# art@artaman.net
#
# Attribution 4.0 International (CC BY 4.0)
# https://creativecommons.org/licenses/by/4.0/
#
# Developed on OSX, should work on random *nix system
# --------------------------------------------------------------
if __name__ == "__main__":
    sys.exit("This is intended to be used within Nuke")

import nuke
import nukescripts
import os, sys
import threading
import operator

estimator_path = os.getenv("HOME") + "/.nuke/estimator"
sys.path.append(estimator_path)
import pyseq
from filesize import size as sconvert

class estimatorPanel(nukescripts.PythonPanel):
        def __init__(self):
            nukescripts.PythonPanel.__init__(
                self,
                'Estimator',
                'uk.co.thefoundry.estimatorPanel')
            self.runBtn = nuke.PyScript_Knob('Run')
            self.precisionValue = nuke.Int_Knob('Frames to calculate: ')
            self.divider = nuke.Text_Knob('')
            self.pathBool = nuke.Boolean_Knob('Show full path')
            self.disabledBool = nuke.Boolean_Knob('Estimate disabled nodes')
            self.sortedBool = nuke.Boolean_Knob('Sort by size')

            self.addKnob(self.precisionValue)
            self.addKnob(self.runBtn)
            self.addKnob(self.divider)
            self.addKnob(self.pathBool)
            self.addKnob(self.disabledBool)
            self.addKnob(self.sortedBool)

            self.precisionValue.setValue(10)
            self.disabledBool.setValue(1)

            self.prj_first_frame = int(nuke.toNode('root').knob('first_frame').value())
            self.prj_last_frame = int(nuke.toNode('root').knob('last_frame').value())
            self.prj_length = abs(self.prj_last_frame - self.prj_first_frame)

            global DEV
            DEV = 0

        def evaluate_script(self, checker=0):
            """
            :param checker: 1 = Regular evaluation, mostly useful from panel itself
                            2 = Return dictionary of parsed 'Read' nodes
            :return: {'/path/to/sequence_%0Xd.xxx': [first_frame, last_frame, size_in_bytes]}
            """
            files_to_check = {}
            readTypes = ('Read', 'DeepRead', 'ReadGeo2')

            def fill_files(N):
                """
                :param N: read node within group/gizmo or directly from DAG
                :return: updated files_to_check or None
                """
                if N.knob('disable').value():
                    if not self.disabledBool.value():
                        return None
                file_path = N.knob('file').value()
                if file_path:
                    if N.Class() == "ReadGeo2":
                        first = int(N.knob('range_first').value())
                        last = int(N.knob('range_last').value())
                    else:
                        first = int(N.knob('first').value())
                        last = int(N.knob('last').value())
                    if "%d" in file_path:
                        numbering = "%0" + str(len(str(last))) + "d"
                        file_path = file_path.replace("%d", numbering)
                    return files_to_check.update({file_path: [first, last]})

            for node in nuke.allNodes():
                if node.knob('gizmo_file') or node.Class() == "Group":
                    for subNode in nuke.toNode(node.name()).nodes():
                        if subNode.Class() in readTypes:
                            if DEV > 1:
                                print "Adding: " + subNode.fullName() + ", class: " + str(subNode.Class())
                                print subNode.knob('file').value() + "\n"
                            fill_files(N=subNode)
                else:
                    if node.Class() in readTypes:
                        if DEV > 1:
                            print "Adding: " + node.fullName() + ", class: " + str(node.Class())
                            print node.knob('file').value() + "\n"
                        fill_files(N=node)

            if checker == 1:
                print "\n~ There are " + str(len(files_to_check)) + " sequences in this script.\n"

            total_size = 0
            seq_errors = 0
            seq_suspicious = 0
            nice_files_to_check = {}
            for sequence, metadata in files_to_check.iteritems():
                    if DEV > 0:
                        print "\n* Sequence: " + sequence
                        print "range: " + str(metadata)
                    seq_padding = "".join(sequence.split("/")[-1].split(".")[:-1])
                    if "%d" in seq_padding:
                        seq_numbering = "%0" + str(len(str(metadata[1]))) + "d"
                        sequence = sequence.replace("%d", seq_numbering)
                        if DEV > 0:
                            print "New sequence name: " + sequence
                    elif "#" in seq_padding:
                        seq_numbering = "%0" + str(seq_padding.count("#")) + "d"
                    elif "%" in seq_padding:
                        seq_numbering = "%" + seq_padding.split("%")[-1]
                    else:
                        seq_numbering = None
                    seq_name_full = sequence + " " + str(metadata[0]) + "-" + str(metadata[1])
                    seq_object = pyseq.uncompress(seq_name_full, format="%h%p%t %r")
                    seq_folder = "/".join(sequence.split("/")[:-1])
                    seq_niceName = sequence.split("/")[-1]
                    seq_size = 0
                    if DEV > 0:
                        print "seq_numbering: " + str(seq_numbering)
                        print "seq_name_full: " + seq_name_full
                        print "seq_object: " + str(seq_object)
                        print "seq_folder: " + seq_folder
                        print "seq_niceName: " + seq_niceName
                    def splitter(a, n):
                        """
                        :param a: divide A
                        :param n: by N parts
                        :return: equally splitted lists
                        """
                        k, m = len(a) / n, len(a) % n
                        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))
                    if seq_object:
                            if metadata[1] - metadata[0] > self.prj_length + 50:
                                seq_suspicious += 1
                            seq_length = int(len(seq_object.frames())) - 1
                            if DEV > 0:
                                print "seq_length: %s" %seq_length
                            if seq_length <= self.precisionValue.value():
                                if seq_length < 2:
                                    seq_frame = seq_object.format('%h') + seq_object.format('%t')
                                    seq_frame_path = os.path.join(seq_folder, seq_frame)
                                    if DEV > 0:
                                        print ".: " + seq_frame_path
                                    if os.path.isfile(seq_frame_path) is True:
                                        seq_size += abs(os.path.getsize(seq_frame_path))
                                    else:
                                        if DEV > 0:
                                            print "\n! something wrong with " + seq_frame_path + "\n"
                                else:
                                    for frame in seq_object.frames():
                                        if seq_numbering:
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
                                calculated = 0
                                split = list(splitter(seq_object.frames(), self.precisionValue.value()))
                                for x in split:
                                    frame = str(x[0]).zfill(int(seq_numbering[2]))
                                    seq_frame = seq_object.format('%h') + frame + seq_object.format('%t')
                                    seq_frame_path = os.path.join(seq_folder, seq_frame)
                                    if os.path.isfile(seq_frame_path) is True:
                                        approx_size += abs(os.path.getsize(seq_frame_path))
                                        calculated += 1
                                    else:
                                        if DEV > 0:
                                            print "\n! something wrong with " + seq_frame_path + "\n"
                                if calculated > 1:
                                    f_approx_size = approx_size / calculated
                                    e_approx_size = f_approx_size * seq_length
                                    seq_size += e_approx_size
                                    if DEV > 0:
                                        print str(e_approx_size) + " = " + str(f_approx_size) + " * " + str(seq_length)
                                else:
                                    seq_size += e_approx_size
                    else:
                        if DEV > 0:
                            print "estimating SINGLE file: " + sequence
                        if os.path.isfile(sequence) is True:
                            seq_size += abs(os.path.getsize(sequence))

                    files_to_check[sequence].append(seq_size)

                    if checker == 1:
                            constr = None
                            if seq_size > 0:
                                if self.pathBool.value() is False:
                                    constr = seq_niceName
                                else:
                                    constr = sequence
                            else:
                                seq_errors += 1
                            if not self.sortedBool.value():
                                if constr:
                                    print "* " + constr + " .... " + sconvert(seq_size)
                            else:
                                if constr:
                                    nice_files_to_check[constr] = files_to_check[sequence]
                            total_size += seq_size

            if self.sortedBool.value():
                for x in nice_files_to_check:
                    nice_files_to_check[x] = nice_files_to_check[x][2]
                sorted_files_to_check = sorted(nice_files_to_check.items(), key=operator.itemgetter(1), reverse=True)
                for x in sorted_files_to_check:
                    print "* " + str(x[0]) + " .... " + sconvert(int(x[1]))

            if checker == 1:
                print "\n~ Total size: " + sconvert(total_size)
                if seq_suspicious > 0:
                    print "~ Suspiciously big sequences: %s" %seq_suspicious
                elif seq_errors > 0:
                    print "! Unreadable read nodes: %s" %seq_errors

            if checker == 2:
                return files_to_check

        def knobChanged(self, knob):
            if knob is self.runBtn:
                threading.Thread(target=self.evaluate_script, args=(1,)).start()
            elif knob is self.precisionValue:
                if self.precisionValue.value() >= self.prj_length-2:
                    self.precisionValue.setValue(self.prj_length)
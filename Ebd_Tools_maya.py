# -*- coding: UTF-8 -*-#

import os
import shutil
import sys
import re

import webbrowser as web

import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtUiTools import QUiLoader
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

Ebd_Tools_Maya = 'False'
for i in sys.path:
    if i.split('/')[-1] == 'Ebd_Tools_Maya' or i.split('\\')[-1] == 'Ebd_Tools_Maya':
        Ebd_Tools_Maya = 'True'
        UIFile = i + "/ui/Ebd_Tools_maya.ui"
        pass
if Ebd_Tools_Maya == 'True':
    pass
elif Ebd_Tools_Maya == 'False':
    for i in sys.path:
        if os.path.exists(i + r"/Ebd_Tools_Maya"):
            sys.path.append(i + r"/Ebd_Tools_Maya")
            sys.path.append(i + r"/Ebd_Tools_Maya/Lib/site_packages")
            UIFile = i + r"/Ebd_Tools_Maya/ui/Ebd_Tools_maya.ui"
        else:
            pass
import maya.cmds as cmds
import zipfile
import wget
import cv2CvtFormat
import cv2SplitAndMergeChanel as cv2ARMS


class EbdToolsMaya(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(EbdToolsMaya, self).__init__(*args, **kwargs)
        self.widget = QUiLoader().load(UIFile)
        self.setCentralWidget(self.widget)
        self.setWindowTitle(self.widget.windowTitle())
        self.create_connections()
        self.setFileIcon()



    # u 绑定按钮


    def create_connections(self):

        # Layout 模块
        self.widget.InstancReplaceButton.clicked.connect(self.InstancReplace)
        self.widget.CopyReplaceButton.clicked.connect(self.CopyReplace)
        self.widget.CombineLoopButton.clicked.connect(self.CombineLoop)
        self.widget.SelectTheSameModelButton.clicked.connect(self.SelectTheSameMesh)
        self.widget.Freeze_Floor_pushButton.clicked.connect(self.autoPlacePivot)

        # Texture模块
        self.widget.txCvtFormatButton.clicked.connect(self.txCvtFormat)
        self.widget.selectExistingFormatButton.clicked.connect(self.selectExistingFormat)
        self.widget.MergeRGBA_Button.clicked.connect(self.MergeRGBA)
        self.widget.SplitRGBA_Button.clicked.connect(self.SplitRGBA)
        self.widget.txRenameButton.clicked.connect(self.txRename)
        self.widget.matAutoLinkButton.clicked.connect(self.RsMatAutoLink)
        self.widget.matAutoLinkTexDirPathButton.clicked.connect(self.matAutoLinkTexDirPathDialog)
        self.widget.procedureCVTtexRunButton.clicked.connect(self.procedureCVTtexRun)
        self.widget.SelectionMatForNormalButton.clicked.connect(self.SelectionMatForNormal)
        self.widget.ConvertNormalToBumpButton.clicked.connect(self.ConvertNormalToBump)

        # selection 模块
        self.widget.SelectUdimTextures_Button.clicked.connect(self.SelectUdimTextures)
        self.widget.SelectNoArmsMats_Button.clicked.connect(self.SelectNoArmsMats)
        self.widget.SimilarUdimTextures_Button.clicked.connect(self.SimilarUdimTextures)
        self.widget.select_TX_for_str_Button.clicked.connect(self.select_TX_for_str)
        self.widget.select_Node_for_str_Button.clicked.connect(self.select_Node_str)


        self.widget.SelectAllMesh_Button.clicked.connect(self.SelectAllMesh)

        #EBD 模块
        self.widget.GetTypeButton.clicked.connect(self.GetType)
        self.widget.ListAttrButton.clicked.connect(self.ListAttr)


        self.widget.UpadateButton.clicked.connect(self.Upadate)
        self.widget.GoHomeButton.clicked.connect(self.GoHome)



    def setFileIcon(self):
        self.widget.matAutoLinkTexDirPathButton.setIcon(QtGui.QIcon(":fileOpen.png"))

    # 创建Dialog对话框
    def matAutoLinkTexDirPathDialog(self):
        matAutoLinkTexDirPath = QtWidgets.QFileDialog.getExistingDirectory(self)
        if matAutoLinkTexDirPath:
            self.widget.matAutoLinkTexDirLineEdit.setText(matAutoLinkTexDirPath)





    # 创建功能模块
    # Layout 模块
    # 实例替换
    def InstancReplace(self):
        # 默认方法实例替换
        if self.widget.InstancReplace_Defult_radioButton.isChecked():
            sele = cmds.ls(sl=1)
            a = 0
            for i in sele:
                if i == sele[-1]:
                    pass
                else:
                    a = a + 1.00
                    cmds.select((cmds.instance(sele[-1]))[0], i)
                    cmds.MatchTransform()
                    self.widget.Replace_progressBar.setValue(a / (len(sele) - 1) * 100)
        # 实例替换_三点对齐
        elif self.widget.InstancReplace_3point_radioButton.isChecked():
            sele = cmds.ls(sl=1)
            a = 0
            zz = []
            for i in sele:
                if i == sele[-1]:
                    pass
                else:
                    aa = cmds.polyEvaluate(i, v=1)
                    bb = cmds.polyEvaluate(sele[-1], v=1)

                    if aa != bb:
                        zz.append(i)
                        pass
                    else:
                        a = a + 1.00
                        cc = aa / 2
                        # 创建实例
                        dd = cmds.instance(sele[-1])

                        # 进行第一次三点对齐
                        cmds.select(dd[0] + '.vtx[0]', dd[0] + '.vtx[' + str(cc) + ']',
                                    dd[0] + '.vtx[' + str(cc - 1) + ']',
                                    i + '.vtx[0]', i + '.vtx[' + str(cc) + ']', i + '.vtx[' + str(cc - 1) + ']')

                        cmds.Snap3PointsTo3Points()
                        # 求缩放值
                        bbox = cmds.exactWorldBoundingBox(dd[0])
                        bbox_a = cmds.exactWorldBoundingBox(i)
                        size = '%.3f' % ((bbox_a[3] - bbox_a[0]) / (bbox[3] - bbox[0])), '%.3f' % (
                                (bbox_a[4] - bbox_a[1]) / (bbox[4] - bbox[1])), '%.3f' % (
                                       (bbox_a[5] - bbox_a[2]) / (bbox[5] - bbox[2]))

                        # 对物体缩放后，二次进行三点捕捉对齐

                        cmds.scale(float(size[0]), float(size[1]), float(size[2]), dd[0], ocp=1, )
                        cmds.Snap3PointsTo3Points()
                        self.widget.Replace_progressBar.setValue(a / (len(sele) - 1) * 100)
            cmds.select(zz)
        # 实例替换_粗略对齐(利用物体的中心点捕捉位置,利用boundingBox大小缩放)
        elif self.widget.InstancReplace_BoundingBox_radioButton.isChecked():
            sel = cmds.ls(sl=True)
            a = 0
            ee = cmds.polyEvaluate(sel[-1], boundingBox=True)
            eex = ee[0][-1] - ee[0][0]
            eey = ee[1][-1] - ee[1][0]
            eez = ee[2][-1] - ee[2][0]
            for i in sel:
                if i == sel[-1]:
                    pass
                else:
                    a = a + 1.00
                    ii = cmds.polyEvaluate(i, boundingBox=True)
                    iix = ii[0][-1] - ii[0][0]
                    iiy = ii[1][-1] - ii[1][0]
                    iiz = ii[2][-1] - ii[2][0]

                    cmds.select((cmds.instance(sel[-1]))[0], i)
                    cmds.MatchTransform()
                    cmds.select(i, toggle=True)
                    cmds.scale(iix / eex, iiy / eey, iiz / eez)
                    self.widget.Replace_progressBar.setValue(a / (len(sel) - 1) * 100)

        # 否则使用默认实例替换
        else:
            sele = cmds.ls(sl=1)
            a = 0
            for i in sele:
                if i == sele[-1]:
                    pass
                else:
                    a = a + 1.00
                    cmds.select((cmds.instance(sele[-1]))[0], i)
                    cmds.MatchTransform()
                    self.widget.Replace_progressBar.setValue(a / (len(sele) - 1) * 100)

    # 复制替换
    def CopyReplace(self):
        # 默认方法_复制替换
        if self.widget.CopyReplace_Defult_radioButton.isChecked():
            sele = cmds.ls(sl=1)
            a = 0
            for i in sele:
                if i == sele[-1]:
                    pass
                else:
                    a = a + 1.00
                    cmds.select((cmds.duplicate(sele[-1]))[0], i)
                    cmds.MatchTransform()
                    self.widget.Replace_progressBar.setValue(a / (len(sele) - 1) * 100)
        # 复制替换_三点捕捉
        elif self.widget.CopyReplace_3point_radioButton.isChecked():
            sele = cmds.ls(sl=1)
            a = 0
            zz = []
            for i in sele:
                if i == sele[-1]:
                    pass
                else:
                    aa = cmds.polyEvaluate(i, v=1)
                    bb = cmds.polyEvaluate(sele[-1], v=1)

                    if aa != bb:
                        zz.append(i)
                        pass
                    else:
                        a = a + 1.00
                        cc = aa / 2
                        # 创建实例
                        dd = cmds.duplicate(sele[-1])

                        # 进行第一次三点对齐
                        cmds.select(dd[0] + '.vtx[0]', dd[0] + '.vtx[' + str(cc) + ']',
                                    dd[0] + '.vtx[' + str(cc - 1) + ']',
                                    i + '.vtx[0]', i + '.vtx[' + str(cc) + ']', i + '.vtx[' + str(cc - 1) + ']')

                        cmds.Snap3PointsTo3Points()
                        # 求缩放值
                        bbox = cmds.exactWorldBoundingBox(dd[0])
                        bbox_a = cmds.exactWorldBoundingBox(i)
                        size = '%.3f' % ((bbox_a[3] - bbox_a[0]) / (bbox[3] - bbox[0])), '%.3f' % (
                                (bbox_a[4] - bbox_a[1]) / (bbox[4] - bbox[1])), '%.3f' % (
                                       (bbox_a[5] - bbox_a[2]) / (bbox[5] - bbox[2]))

                        # 对物体缩放后，二次进行三点捕捉对齐

                        cmds.scale(float(size[0]), float(size[1]), float(size[2]), dd[0], ocp=1, )
                        cmds.Snap3PointsTo3Points()
                        self.widget.Replace_progressBar.setValue(a / (len(sele) - 1) * 100)
            cmds.select(zz)
        # 复制替换_根据bound ingBox的大小
        elif self.widget.InstancReplace_BoundingBox_radioButton.isChecked():
            sel = cmds.ls(sl=True)
            a = 0
            ee = cmds.polyEvaluate(sel[-1], boundingBox=True)
            eex = ee[0][-1] - ee[0][0]
            eey = ee[1][-1] - ee[1][0]
            eez = ee[2][-1] - ee[2][0]
            for i in sel:
                if i == sel[-1]:
                    pass
                else:
                    a = a + 1.00
                    ii = cmds.polyEvaluate(i, boundingBox=True)
                    iix = ii[0][-1] - ii[0][0]
                    iiy = ii[1][-1] - ii[1][0]
                    iiz = ii[2][-1] - ii[2][0]

                    cmds.select((cmds.duplicate(sel[-1]))[0], i)
                    cmds.MatchTransform()
                    cmds.select(i, toggle=True)
                    cmds.scale(iix / eex, iiy / eey, iiz / eez)
                    self.widget.Replace_progressBar.setValue(a / (len(sel) - 1) * 100)
        # 复制替换_根据点序号 逐点拓扑
        elif self.widget.CopyReplace_Topology_radioButton.isChecked():
            sele = cmds.ls(sl=1)
            a = 0
            zz = []
            for c in sele:
                if c == sele[-1]:
                    pass
                else:
                    a = a + 1.00
                    aa = cmds.polyEvaluate(c, v=1)
                    bb = cmds.polyEvaluate(sele[-1], v=1)
                    if aa != bb:
                        self.widget.EbdLog_Browser.append("与目标多边形点数不同,请手动对齐对象或者使用坐标轴")
                        self.widget.EbdLog_Browser.ensureCursorVisible()
                        zz.append(c)
                        pass
                    else:
                        # 复制源物体
                        ee = cmds.duplicate(sele[-1])
                        # 循环匹配复制的源物体的每个顶点
                        for d in range(bb):
                            # 求目标物体点位置
                            ff = cmds.pointPosition(c + '.vtx[' + str(d) + ']', w=1)
                            # 移动源点到目标物体点位置
                            cmds.xform(ee[0] + '.vtx[' + str(d) + ']', ws=1, t=ff)
                        self.widget.Replace_progressBar.setValue(a / (len(sele) - 1) * 100)
            cmds.select(zz)
            self.widget.EbdLog_Browser.append(cmds.warning('与目标多边形点数不同,请手动对齐对象或者使用坐标轴，使用实例替换试试'))
            self.widget.EbdLog_Browser.ensureCursorVisible()
        else:
            sele = cmds.ls(sl=1)
            a = 0
            for i in sele:
                if i == sele[-1]:
                    pass
                else:
                    a = a + 1.00
                    cmds.select((cmds.duplicate(sele[-1]))[0], i)
                    cmds.MatchTransform()
                    self.widget.Replace_progressBar.setValue(a / (len(sele) - 1) * 100)

    # 循环合并选择的组
    def CombineLoop(self):
        sele = cmds.ls(sl=1)
        a = 0
        aa = []
        for i in sele:
            a = a + 1.00
            cmds.polyUnite(i)
            cmds.delete(constructionHistory=True)
            self.widget.CombineLoop_progressBar.setValue(a / len(sele) * 100)
        print (aa)

    # 选择相似模型
    def SelectTheSameMesh(self):
        sel = cmds.ls(sl=True)
        aa = self.widget.Vtx_Offest_Same_Mesh_spinBox.value()
        bb = self.widget.UV_Offest_Same_Mesh_spinBox.value()
        ff = cmds.polyEvaluate(sel[-1], vertex=True)
        jj = cmds.polyEvaluate(sel[-1], uvShell=True)
        gg = []
        hh = cmds.ls(sl=True)
        for i in hh:
            ii = cmds.polyEvaluate(i, vertex=True)
            kk = cmds.polyEvaluate(i, uvShell=True)

            if ff - aa <= ii <= ff + aa:
                if self.widget.Uv_Same_Mesh_checkBox.isChecked():
                    if jj - bb <= kk <= jj + bb:
                        gg.append(i)
                else:
                    gg.append(i)
        if self.widget.Select_Same_Mesh_radioButton.isChecked():
            cmds.select(gg)
        elif self.widget.Group_Same_Mesh_radioButton.isChecked():
            cmds.select(gg)
            cmds.Group()
        else:
            cmds.select(gg)

    # 冻结位移数据并归世界中心
    def autoPlacePivot(self):
        sele = cmds.ls(sl=1)
        if len(sele) != 0:
            cmds.xform(sele, cp=1)
            bbox = cmds.exactWorldBoundingBox()
            bottom = [(bbox[0] + bbox[3]) / 2, bbox[1], (bbox[2] + bbox[5]) / 2]
            cmds.xform(sele, piv=bottom, ws=1)
            cmds.move(0, 0, 0, sele, rpr=1)
            if self.widget.Freeze_checkBox.isChecked():
                cmds.makeIdentity(sele, apply=1, t=1, r=1, s=1, n=0)

    # Texture模块

    # 批量转换redshift 的 normal 节点 到 bumpNormal节点

    # 筛选符合转换条件的节点
    # 贴图格式批量转换
    def selectExistingFormat(self):
        sele = []
        newSele = []
        Format = self.widget.existingFormatComboBox.currentText()
        sele = cmds.ls(sl=1,type = 'file')
        if len(sele) == 0:
            sele = cmds.ls(type='file')

        for c in sele:
            Path = cmds.getAttr(c+'.ftn',asString=1)
            if Path.split('\\')[-1].split('.')[-1].lower() == Format:
                newSele.append(c)
                pass
            else:
                pass
        if len(newSele) == 0:
            self.widget.EbdLog_Browser.append("warning 没有找到要转换的file节点")
            self.widget.EbdLog_Browser.ensureCursorVisible()
        else:
            cmds.select(newSele)

    def txCvtFormat(self):
        sele = cmds.ls(sl=1)
        targetFormat = self.widget.targetFormatComboBox.currentText()
        existingFormat = self.widget.existingFormatComboBox.currentText()
        backupFilePath = cmds.workspace(fullName=True) + '/sourceimages/' + 'backupFile/'

        # 创建备份文件夹到工程目录
        if os.path.exists(backupFilePath):
            pass
        else:
            os.makedirs(backupFilePath)

        # 图片格式是否正确
        if targetFormat == existingFormat:
            self.widget.EbdLog_Browser.append(" warning 请设置要转换的格式 并重试")
            self.widget.EbdLog_Browser.ensureCursorVisible()
            pass
        else:
            pass

        # 将选出的贴图 去UDIM化
        udimList = []
        normalFilePathList = []
        seleFilePathList = []
        self.widget.EbdLog_Browser.append("获取选择file节点的绝对路径并修改新的绝对路径")
        self.widget.EbdLog_Browser.ensureCursorVisible()
        if '16' in targetFormat:
            FileNodetargetFormat = targetFormat[:-2]
        else:
            FileNodetargetFormat = targetFormat
        for i in sele:
            FilePath = cmds.getAttr(i + '.ftn', asString=1)
            seleFilePathList.append(FilePath)
            newFilePath = FilePath[:len(FilePath.split('.')[-1]) * -1] + FileNodetargetFormat
            cmds.setAttr(i + '.ftn', newFilePath, type='string')
        self.widget.EbdLog_Browser.append("file节点路径更新完成，进行分类UDIM贴图与普通贴图")
        self.widget.EbdLog_Browser.ensureCursorVisible()
        for i in seleFilePathList:
            fileAbsName = i.split('\\')[-1]
            normalFilePathList.append(i)
            for a in range(1001, 1101):
                if str(a) in fileAbsName:
                    normalFilePathList.pop(-1)
                    for b in range(1001, 1101):
                        fielUdimName = i[:len(fileAbsName) * -1] + (fileAbsName.split(str(a)))[0] + str(b) + \
                                       (fileAbsName.split(str(a)))[-1]
                        if os.path.exists(fielUdimName):
                            udimList.append(fielUdimName)
                        else:
                            pass
                    break
        self.widget.EbdLog_Browser.append("贴图分类完成,进行贴图格式转换")
        self.widget.EbdLog_Browser.ensureCursorVisible()
        # 将贴图转进行格式转换
        for i in (udimList + normalFilePathList):
            cv2CvtFormat.ConverterFormat(i, targetFormat)
        self.widget.EbdLog_Browser.append("格式转换完成,进行备份")
        self.widget.EbdLog_Browser.ensureCursorVisible()
        for i in (udimList + normalFilePathList):
            shutil.copy(i, backupFilePath)
            os.remove(i)
        self.widget.EbdLog_Browser.append("贴图格式转换程序已经运行完毕,请进行检查")
        self.widget.EbdLog_Browser.append("备份文件夹地址'+backupFilePath")
        self.widget.EbdLog_Browser.ensureCursorVisible()


    # 贴图重命名
    def txRename(self):
        shading = cmds.ls(sl=True)[0]
        backupFilePath = cmds.workspace(fullName=True) + '/sourceimages/' + 'backupFile/'
        newFileName = self.widget.txRename_lineEdit.text()
        # 创建备份文件夹到工程目录
        if os.path.exists(backupFilePath):
            pass
        else:
            os.makedirs(backupFilePath)

        # BaseColor
        BaseColor_Node = cmds.listConnections(shading + '.diffuse_color', type='file')
        # ReflRoughness_Node
        ReflRoughness_Node = cmds.listConnections(shading + '.refl_roughness', type='file')

        # ReflMetalness_Node
        ReflMetalness_Node = cmds.listConnections(shading + '.refl_metalness', type='file')
        # RsNormal_Node
        RsNormal_Node = cmds.listConnections(shading + '.bump_input', type='RedshiftNormalMap')
        # RsBump
        RsBump = cmds.listConnections(shading + '.bump_input', type='RedshiftBumpMap')
        if RsBump is None:
            RsBump_Node = None
            pass
        else:
            RsBump_Node = cmds.listConnections(RsBump[0] + '.input', type='file')
        # EmissColor_Node
        EmissColor_Node = cmds.listConnections(shading + '.emission_color', type='file')
        # OpacityColor_Node
        OpacityColor_Node = cmds.listConnections(shading + '.opacity_color', type='file')
        # ARMS_Node
        if (ReflRoughness_Node != None or ReflMetalness_Node != None) and ReflRoughness_Node == ReflMetalness_Node:
            haveARMS_Node = True
        else:
            haveARMS_Node = False
            pass
        #

        if BaseColor_Node is None:
            pass
        else:
            oldFile = cmds.getAttr(BaseColor_Node[0] + '.computedFileTextureNamePattern')
            oldFilePath = oldFile[:len(oldFile.split('/')[-1])*-1]

            Format = oldFile.split(".")[-1]
            if '<UDIM>' in oldFile:
                isUdim = True
                udimNum = '1001'
                for b in range(1001, 1101):
                    oldUdimFile = oldFile.split('<UDIM>')[0] + str(b) + oldFile.split('<UDIM>')[-1]
                    if os.path.exists(oldUdimFile):
                        NewUdimFile = oldFilePath + newFileName + '_BaseColor' + '_' + str(b) + '.' + Format
                        shutil.copy(oldUdimFile, backupFilePath)
                        os.rename(oldUdimFile, NewUdimFile)
            else:
                isUdim = False

            if isUdim == False:
                newFile = oldFilePath + newFileName + '_BaseColor' + '.' + Format
                shutil.copy(oldFile, backupFilePath)
                os.rename(oldFile, newFile)
            else:
                newFile = oldFilePath + newFileName + '_BaseColor' + '_' + udimNum + '.' + Format
            print(newFile)
            cmds.setAttr(BaseColor_Node[0] + '.fileTextureName', newFile, type="string")

        if ReflRoughness_Node == None and haveARMS_Node == True:
            pass
        elif ReflRoughness_Node == None and haveARMS_Node == False:
            pass
        else:
            oldFile = cmds.getAttr(ReflRoughness_Node[0] + '.computedFileTextureNamePattern')
            oldFilePath = oldFile[:len(oldFile.split('/')[-1]) * -1]
            Format = oldFile.split(".")[-1]
            isUdim = False

            if '<UDIM>' in oldFile:
                isUdim = True
                udimNum = '1001'

                for b in range(1001, 1101):
                    oldUdimFile = oldFile.split('<UDIM>')[0] + str(b) + oldFile.split('<UDIM>')[-1]
                    if os.path.exists(oldUdimFile):
                        NewUdimFile = oldFilePath + newFileName + '_Roughness' + '_' + str(b) + '.' + Format
                        shutil.copy(oldUdimFile, backupFilePath)
                        os.rename(oldUdimFile, NewUdimFile)
            else:
                isUdim = False
            if isUdim == False:
                newFile = oldFilePath + newFileName + '_Roughness' + '.' + Format
                shutil.copy(oldFile, backupFilePath)
                os.rename(oldFile, newFile)
            else:
                newFile = oldFilePath + newFileName + '_Roughness' + '_' + udimNum + '.' + Format
            cmds.setAttr(ReflRoughness_Node[0] + '.fileTextureName', newFile, type="string")

        #
        if ReflMetalness_Node == None and haveARMS_Node == True:
            pass
        elif ReflMetalness_Node == None and haveARMS_Node == False:
            pass
        else:
            pass
            oldFile = cmds.getAttr(ReflMetalness_Node[0] + '.computedFileTextureNamePattern')
            oldFilePath = oldFile[:len(oldFile.split('/')[-1]) * -1]
            Format = oldFile.split(".")[-1]
            if '<UDIM>' in oldFile:
                isUdim = True
                udimNum = '1001'

                for b in range(1001, 1101):
                    oldUdimFile = oldFile.split('<UDIM>')[0] + str(b) + oldFile.split('<UDIM>')[-1]
                    if os.path.exists(oldUdimFile):
                        NewUdimFile = oldFilePath + newFileName + '_Metallic' + '_' + str(b) + '.' + Format
                        shutil.copy(oldUdimFile, backupFilePath)
                        os.rename(oldUdimFile, NewUdimFile)
            else:
                isUdim = False
            if isUdim == False:
                newFile = oldFilePath + newFileName + '_Metallic' + '.' + Format
                shutil.copy(oldFile, backupFilePath)
                os.rename(oldFile, newFile)
            else:
                newFile = oldFilePath + newFileName + '_Metallic' + '_' + udimNum + '.' + Format
            cmds.setAttr(ReflMetalness_Node[0] + '.fileTextureName', newFile, type="string")
        #
        if RsNormal_Node is None:
            pass
        else:
            self.widget.EbdLog_Browser.append("检测到材质球下有RsNormalMap节点，请转换为RsBumpMap节点后重试")
            self.widget.EbdLog_Browser.ensureCursorVisible()
        #
        if RsBump_Node is None:
            pass
        else:
            oldFile = cmds.getAttr(RsBump_Node[0] + '.computedFileTextureNamePattern')
            oldFilePath = oldFile[:len(oldFile.split('/')[-1]) * -1]
            Format = oldFile.split(".")[-1]

            if '<UDIM>' in oldFile:
                isUdim = True
                udimNum = '1001'
                for b in range(1001, 1101):
                    oldUdimFile = oldFile.split('<UDIM>')[0] + str(b) + oldFile.split('<UDIM>')[-1]
                    if os.path.exists(oldUdimFile):
                        NewUdimFile = oldFilePath + newFileName + '_Normal' + '_' + str(b) + '.' + Format
                        shutil.copy(oldUdimFile, backupFilePath)
                        os.rename(oldUdimFile, NewUdimFile)
            else:
                isUdim = False
            if isUdim == False:
                newFile = oldFilePath + newFileName + '_Normal' + '.' + Format
                shutil.copy(oldFile, backupFilePath)
                os.rename(oldFile, newFile)
            else:
                newFile = oldFilePath + newFileName + '_Normal' + '_' + udimNum + '.' + Format
            cmds.setAttr(RsBump_Node[0] + '.fileTextureName', newFile, type="string")

        #
        if EmissColor_Node is None:
            pass
        else:
            oldFile = cmds.getAttr(EmissColor_Node[0] + '.computedFileTextureNamePattern')
            oldFilePath = oldFile[:len(oldFile.split('/')[-1]) * -1]
            Format = oldFile.split(".")[-1]


            if '<UDIM>' in oldFile:
                isUdim = True
                udimNum = '1001'

                for b in range(1001, 1101):
                    oldUdimFile = oldFile.split('<UDIM>')[0] + str(b) + oldFile.split('<UDIM>')[-1]
                    if os.path.exists(oldUdimFile):
                        NewUdimFile = oldFilePath + newFileName + '_Emissive' + '_' + str(b) + '.' + Format
                        shutil.copy(oldUdimFile, backupFilePath)
                        os.rename(oldUdimFile, NewUdimFile)
            else:
                isUdim = False
            if isUdim == False:
                newFile = oldFilePath + newFileName + '_Emissive' + '.' + Format
                shutil.copy(oldFile, backupFilePath)
                os.rename(oldFile, newFile)
            else:
                newFile = oldFilePath + newFileName + '_Emissive' + '_' + udimNum + '.' + Format
            cmds.setAttr(EmissColor_Node[0] + '.fileTextureName', newFile, type="string")

        #
        if OpacityColor_Node is None:
            pass
        else:
            oldFile = cmds.getAttr(OpacityColor_Node[0] + '.computedFileTextureNamePattern')
            oldFilePath = oldFile[:len(oldFile.split('/')[-1]) * -1]
            Format = oldFile.split(".")[-1]


            if '<UDIM>' in oldFile:
                isUdim = True
                udimNum = '1001'

                for b in range(1001, 1101):
                    oldUdimFile = oldFile.split('<UDIM>')[0] + str(b) + oldFile.split('<UDIM>')[-1]
                    if os.path.exists(oldUdimFile):
                        NewUdimFile = oldFilePath + newFileName + '_Opacity' + '_' + str(b) + '.' + Format
                        shutil.copy(oldUdimFile, backupFilePath)
                        os.rename(oldUdimFile, NewUdimFile)
            else:
                isUdim = False
            if isUdim == False:
                newFile = oldFilePath + newFileName + '_Opacity' + '.' + Format
                shutil.copy(oldFile, backupFilePath)
                os.rename(oldFile, newFile)
            else:
                newFile = oldFilePath + newFileName + '_Opacity' + '_' + udimNum + '.' + Format
            cmds.setAttr(OpacityColor_Node[0] + '.fileTextureName', newFile, type="string")

        if haveARMS_Node == False:
            pass
        else:
            ARMS_Node = ReflRoughness_Node
            oldFile = cmds.getAttr(ARMS_Node[0] + '.computedFileTextureNamePattern')
            oldFilePath = oldFile[:len(oldFile.split('/')[-1]) * -1]
            Format = oldFile.split(".")[-1]


            if '<UDIM>'in oldFile:
                isUdim = True
                udimNum = '1001'

                for b in range(1001, 1101):
                    oldUdimFile = oldFile.split('<UDIM>')[0] + str(b) + oldFile.split('<UDIM>')[-1]
                    if os.path.exists(oldUdimFile):
                        NewUdimFile = oldFilePath + newFileName + '_ARMS' + '_' + str(b) + '.' + Format
                        shutil.copy(oldUdimFile, backupFilePath)
                        os.rename(oldUdimFile, NewUdimFile)
            else:
                isUdim = False
            if isUdim == False:
                newFile = oldFilePath + newFileName + '_ARMS' + '.' + Format
                shutil.copy(oldFile, backupFilePath)
                os.rename(oldFile, newFile)
            else:
                newFile = oldFilePath + newFileName + '_ARMS' + '_' + udimNum + '.' + Format
            cmds.setAttr(ARMS_Node[0] + '.fileTextureName', newFile, type="string")


    #程序性节点转纹理
    def procedureCVTtexRun(self):
        fileName = self.widget.procedureCVTtexLineEdit.text()
        fileSize =  self.widget.procedureCVTtexSizeComboBox.currentText()
        fileFormat = self.widget.procedureCVTtexFormatComboBox.currentText()
        def procedureCVTtex(tarName, tarSize, tarFormat):
            global newtexAbsPath
            # procedureCVTtex('gaga',1024,'jpg')

            melName = '"' + tarName + '"'
            texSize = str(tarSize) + ' ' + str(tarSize) + ' '
            melC = 'composite ' + texSize + melName + ' ' + tarFormat + ' ' + 'images ' + '0 0 1 4 1;'
            mel.eval(melC)
            oldTexPath = cmds.workspace(fullName=True) + '/images/' + tarName + '.0000' + '.' + tarFormat
            newtexPath = cmds.workspace(fullName=True) + '/images/' + tarName + '.' + tarFormat
            newtexAbsPath = cmds.workspace(fullName=True) + '/sourceimages/' + tarName + '.' + tarFormat
            newtexDirPath = cmds.workspace(fullName=True) + '/sourceimages/'
            if os.path.exists(newtexPath):
                os.remove(newtexPath)
            if os.path.exists(newtexAbsPath):
                os.remove(newtexAbsPath)
            os.rename(oldTexPath, newtexPath)
            shutil.move(newtexPath, newtexDirPath)

        sele = cmds.ls(sl=1)
        seleS = cmds.listConnections(sele[0], c=1)
        ShaderInput = []
        TexOut = []
        seleLink = len(seleS)
        for i in range(0, seleLink, 2):
            if '.message' in seleS[i] or 'materialInfo' in seleS[i] or 'hyperShadePrimaryNodeEditorSavedTabsInfo' in \
                    seleS[i] or 'ShaderList' in seleS[i] or '.outColor' in seleS[i] or 'SG' in seleS[i]:
                pass
            else:
                ShaderInput.append(seleS[i])
        for i in range(1, seleLink, 2):
            if '.message' in seleS[i] or 'materialInfo' in seleS[i] or 'hyperShadePrimaryNodeEditorSavedTabsInfo' in \
                    seleS[i] or 'ShaderList' in seleS[i] or '.outColor' in seleS[i] or 'SG' in seleS[i]:
                pass
            else:
                TexOut.append(seleS[i])

        ErDTxtName = fileName + '_tex_2d'
        if ErDTxtName in cmds.ls(type='place2dTexture'):
            self.widget.EbdLog_Browser.append(" error '场景内已经有此名称的节点，换个名字试一试'")
            self.widget.EbdLog_Browser.ensureCursorVisible()
        cmds.shadingNode('place2dTexture', asUtility=True, name=ErDTxtName)
        UVFile = ['outUV', 'uvCoord', 'outUvFilterSize', 'uvFilterSize', 'coverage', 'coverage', 'translateFrame',
                  'translateFrame', 'rotateFrame', 'rotateFrame', 'mirrorU', 'mirrorU', 'mirrorV', 'mirrorV', 'stagger',
                  'stagger', 'wrapU', 'wrapU', 'wrapV', 'wrapV', ' repeatUV', 'repeatUV', 'vertexUvOne', 'vertexUvOne',
                  'vertexUvTwo', 'vertexUvTwo', 'vertexUvThree', 'vertexUvThree', 'vertexCameraOne', 'vertexCameraOne',
                  'noiseUV', 'noiseUV', 'offset', 'offset', 'rotateUV', 'rotateUV']
        a = -1
        for i in ShaderInput:
            a += 1
            cmds.select(TexOut[a])
            if i.split('.')[-1] == 'diffuse_color':
                newTarTex_suffix = '_BaseColor'
            elif i.split('.')[-1] == 'refl_roughness':
                newTarTex_suffix = '_Roughness'
            elif i.split('.')[-1] == 'refl_metalness':
                newTarTex_suffix = '_Metallic'
            elif i.split('.')[-1] == 'opacity_color':
                newTarTex_suffix = '_Opacity'
            elif i.split('.')[-1] == 'emission_color':
                newTarTex_suffix = '_Emissive'
            else:
                self.widget.EbdLog_Browser.append(" warning 程序只支持 BaseColor、Roughness、Metallic、Opacity、Emissive")
                self.widget.EbdLog_Browser.ensureCursorVisible()
                pass


            procedureCVTtex(fileName + newTarTex_suffix, int(fileSize), fileFormat)
            # 创建File文件
            cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=fileName + newTarTex_suffix)
            cmds.setAttr(fileName + newTarTex_suffix + '.fileTextureName', newtexAbsPath, type="string")
            cmds.setAttr(fileName + newTarTex_suffix + '.ignoreColorSpaceFileRules', 1)
            if ('Roughness' or 'Metallic') in newTarTex_suffix:
                cmds.setAttr(fileName + newTarTex_suffix + '.alphaIsLuminance', 1)

            aa = len(UVFile)
            UV = []
            FILE = []
            for d in range(0, aa, 2):
                UV.append(UVFile[d])
            for b in range(1, aa, 2):
                FILE.append(UVFile[b])
            bb = len(UV)
            for c in range(0, bb):
                cmds.connectAttr(ErDTxtName + '.' + UV[c], fileName + newTarTex_suffix + '.' + FILE[c])

            if ('Roughness' or 'Metallic') in newTarTex_suffix:
                cmds.connectAttr(fileName + newTarTex_suffix + '.outAlpha', str(i), f=1)
            else:
                cmds.connectAttr(fileName + newTarTex_suffix + '.outColor', str(i), f=1)

    # 设置返回命令


    #材质球自动链接
    def RsMatAutoLink(self):
        fileName = self.widget.matNameLineEdit.text()
        fileTexPath = self.widget.matAutoLinkTexDirLineEdit.text()
        Format = self.widget.formatComboBox.currentText()
        texModel = self.widget.texModelComboBox.currentText()
        matModel = self.widget.matModelComboBox.currentText()
        displacementIsCheck = self.widget.displacementCheck.isChecked()
        udimIsCheck = self.widget.udimCheck.isChecked()
        opacityIsCheck = self.widget.opacityCheck.isChecked()
        emissionIsCheck = self.widget.emissionCheck.isChecked()

        # 功能模块
        ErDTxtName = fileName + '_tex_2d'
        shaderName = fileName + '_Shader'
        ARMSName = fileName + '_ARMS'
        BaseColorName = fileName + '_BaseColor'
        BumpName = fileName + '_NormalNode'
        BumpTxName = fileName + '_Normal'
        OpacityName = fileName + '_Opacity'
        RoughnessName = fileName + '_Roughness'
        EmissionName = fileName + '_Emissive'
        MetallicName = fileName + '_Metallic'
        DisplacementNode = fileName + '_HeightNode'
        DisplacementName = fileName + '_Height'
        if udimIsCheck:
            udimNum = '_1001'
        else:
            udimNum = ''
        # 列出选择物体
        sele = cmds.ls(sl=True)

        if matModel == 'RsMaterial':

            # 创建redshift材质球
            cmds.shadingNode('RedshiftMaterial', asShader=True, name=shaderName)
            cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName + 'SG')
            cmds.setAttr(shaderName + '.refl_brdf', 1)
            cmds.setAttr(shaderName + '.refl_fresnel_mode', 2)
            if emissionIsCheck:
                cmds.setAttr(shaderName + '.emission_weight', 1)
        elif matModel == 'usdPreviewSurface':
            #创建usdPreviewSurface材质球
            cmds.shadingNode('RedshiftMaterial', asShader=True, name=shaderName)
            cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName + 'SG')
            cmds.setAttr(shaderName + '.refl_brdf', 1)
            cmds.setAttr(shaderName + '.refl_fresnel_mode', 2)
            if emissionIsCheck:
                cmds.setAttr(shaderName + '.emission_weight', 1)

        # # 创建ARMS_file or roughness_file and metlicc_file
        if texModel == 'PBR_ARMS':
            cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=ARMSName, )
            cmds.setAttr(ARMSName + '.fileTextureName', fileTexPath + '/' + ARMSName + udimNum + Format, type="string")
            cmds.setAttr(ARMSName + '.ignoreColorSpaceFileRules', 1)
            cmds.setAttr(ARMSName + '.colorSpace', 'Raw', type='string')
            if udimIsCheck:
                cmds.setAttr(ARMSName + '.uvTilingMode', 3)

        elif texModel == 'PBR_MetallRough':
            cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=RoughnessName, )
            cmds.setAttr(RoughnessName + '.fileTextureName', fileTexPath + '/' + RoughnessName + udimNum + Format, type="string")
            cmds.setAttr(RoughnessName + '.ignoreColorSpaceFileRules', 1)
            cmds.setAttr(RoughnessName + '.colorSpace', 'Raw', type='string')
            cmds.setAttr(RoughnessName + '.alphaIsLuminance', 1)
            if udimIsCheck:
                cmds.setAttr(RoughnessName + '.uvTilingMode', 3)

            cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=MetallicName, )
            cmds.setAttr(MetallicName + '.fileTextureName', fileTexPath + '/' + MetallicName + udimNum + Format, type="string")
            cmds.setAttr(MetallicName + '.ignoreColorSpaceFileRules', 1)
            cmds.setAttr(MetallicName + '.colorSpace', 'Raw', type='string')
            cmds.setAttr(MetallicName + '.alphaIsLuminance', 1)
            if udimIsCheck:
                cmds.setAttr(MetallicName + '.uvTilingMode', 3)


        # 创建Basecolor文件
        cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=BaseColorName, )
        cmds.setAttr(BaseColorName + '.fileTextureName', fileTexPath + '/' + BaseColorName + udimNum + Format, type="string")
        cmds.setAttr(BaseColorName + '.ignoreColorSpaceFileRules', 1)
        if udimIsCheck:
            cmds.setAttr(BaseColorName + '.uvTilingMode', 3)

        #创建normal文件
        cmds.shadingNode('RedshiftBumpMap', asTexture=True, isColorManaged=True, name=BumpName, )
        cmds.setAttr(BumpName + ".inputType", 1)
        cmds.setAttr(BumpName + ".scale", 1)
        cmds.setAttr(BumpName + ".flipY", 1)

        cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=BumpTxName, )
        cmds.setAttr(BumpTxName + '.fileTextureName', fileTexPath + '/' + BumpTxName + udimNum + Format, type="string")
        cmds.setAttr(BumpTxName + '.ignoreColorSpaceFileRules', 1)
        cmds.setAttr(BumpTxName + '.colorSpace', 'Raw', type='string')
        if udimIsCheck:
            cmds.setAttr(BumpTxName + '.uvTilingMode', 3)

        # #
        # 创建 opacity
        if opacityIsCheck :
            cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=OpacityName, )
            cmds.setAttr(OpacityName + '.fileTextureName', fileTexPath + '/' + OpacityName + udimNum + Format, type="string")
            cmds.setAttr(OpacityName + '.ignoreColorSpaceFileRules', 1)
            cmds.setAttr(OpacityName + '.colorSpace', 'Raw', type='string')
            if udimIsCheck:
                cmds.setAttr(OpacityName + '.uvTilingMode', 3)


        if emissionIsCheck :
            cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=EmissionName, )
            cmds.setAttr(EmissionName + '.fileTextureName', fileTexPath + '/' + EmissionName + udimNum + Format, type="string")
            cmds.setAttr(EmissionName + '.ignoreColorSpaceFileRules', 1)
            if udimIsCheck:
                cmds.setAttr(EmissionName + '.uvTilingMode', 3)

        if displacementIsCheck :
            cmds.shadingNode('RedshiftDisplacement', asShader=True, isColorManaged=True, name=DisplacementNode, )
            cmds.setAttr(DisplacementNode + ".map_encoding", 2)
            cmds.setAttr(DisplacementNode + ".newrange_min", -0.5)
            cmds.setAttr(DisplacementNode + ".newrange_max", 0.5)


            cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=DisplacementName, )
            cmds.setAttr(DisplacementName + '.fileTextureName', fileTexPath + '/' +DisplacementName + udimNum + Format, type="string")
            cmds.setAttr(DisplacementName + '.ignoreColorSpaceFileRules', 1)
            cmds.setAttr(DisplacementName + '.colorSpace', 'Raw', type='string')
            if udimIsCheck:
                cmds.setAttr(DisplacementName + '.uvTilingMode', 3)

        #
        # 创建2dTexture节点
        cmds.shadingNode('place2dTexture', asUtility=True , name = ErDTxtName)

        #链接 2dtex file链接
        UVFile = ['outUV', 'uvCoord', 'outUvFilterSize', 'uvFilterSize', 'coverage', 'coverage', 'translateFrame',
                  'translateFrame', 'rotateFrame', 'rotateFrame', 'mirrorU', 'mirrorU', 'mirrorV', 'mirrorV', 'stagger',
                  'stagger', 'wrapU', 'wrapU', 'wrapV', 'wrapV', ' repeatUV', 'repeatUV', 'vertexUvOne', 'vertexUvOne',
                  'vertexUvTwo', 'vertexUvTwo', 'vertexUvThree', 'vertexUvThree', 'vertexCameraOne', 'vertexCameraOne',
                  'noiseUV', 'noiseUV', 'offset', 'offset', 'rotateUV', 'rotateUV']
        aa = len(UVFile)
        UV = []
        FILE = []
        for i in range(0, aa, 2):
            UV.append(UVFile[i])
        for b in range(1, aa, 2):
            FILE.append(UVFile[b])
        bb = len(UV)
        for c in range(0, bb):
            cmds.connectAttr(ErDTxtName + '.' + UV[c], BaseColorName + '.' + FILE[c])
            cmds.connectAttr(ErDTxtName + '.' + UV[c], BumpTxName + '.' + FILE[c])
            if opacityIsCheck:
                cmds.connectAttr(ErDTxtName + '.' + UV[c], OpacityName + '.' + FILE[c])
            if texModel == 'PBR_ARMS':
                cmds.connectAttr(ErDTxtName + '.' + UV[c], ARMSName + '.' + FILE[c])
            if texModel == 'PBR_MetallRough':
                cmds.connectAttr(ErDTxtName + '.' + UV[c], RoughnessName + '.' + FILE[c])
                cmds.connectAttr(ErDTxtName + '.' + UV[c], MetallicName + '.' + FILE[c])
            if displacementIsCheck:
                cmds.connectAttr(ErDTxtName + '.' + UV[c], DisplacementName + '.' + FILE[c])
            if emissionIsCheck:
                cmds.connectAttr(ErDTxtName + '.' + UV[c], EmissionName + '.' + FILE[c])




        # 链接file到shader
        cmds.connectAttr(BaseColorName + '.outColor', shaderName + '.diffuse_color')
        cmds.connectAttr(BumpTxName + '.outColor', BumpName + '.input')
        cmds.connectAttr(BumpName + '.out', shaderName + '.bump_input')

        if opacityIsCheck:
            cmds.connectAttr(OpacityName + '.outColor', shaderName + '.opacity_color')
        if emissionIsCheck:
            cmds.connectAttr(EmissionName + '.outColor', shaderName + '.emission_color')
        if displacementIsCheck:
            cmds.connectAttr(DisplacementName+ '.outColor', DisplacementNode + '.texMap')
        if texModel == 'PBR_ARMS':
            cmds.connectAttr(ARMSName + '.outColorG', shaderName + '.refl_roughness')
            cmds.connectAttr(ARMSName + '.outColorB', shaderName + '.refl_metalness')
        if texModel == 'PBR_MetallRough':
            cmds.connectAttr(RoughnessName + '.outAlpha', shaderName + '.refl_roughness')
            cmds.connectAttr(MetallicName + '.outAlpha', shaderName + '.refl_metalness')

        # 链接shader到着色组上
        cmds.connectAttr(shaderName + '.outColor', shaderName + 'SG.surfaceShader')
        if displacementIsCheck:
            cmds.connectAttr(DisplacementNode + '.out', shaderName + 'SG.rsDisplacementShader')
        # 链接选择物体到着色组里
        if displacementIsCheck:
            for i in sele:
                seleShapes = cmds.listRelatives(i, shapes=1)
                for e in seleShapes:
                    cmds.setAttr(e + '.rsEnableSubdivision',1)
                    cmds.setAttr(e + '.rsEnableDisplacement',1)
        cmds.select(sele)
        cmds.sets(forceElement=shaderName + 'SG')

    # Ao/roughness/matellic/Opacity 通道拆分hebing
    def MergeRGBA(self):
        sele = cmds.ls(sl=1)
        backupFilePath = cmds.workspace(fullName=True) + '/sourceimages/' + 'backupFile/'

        # 创建备份文件夹到工程目录
        if os.path.exists(backupFilePath):
            pass
        else:
            os.makedirs(backupFilePath)

        for i in sele:
            #  ReflMetalness_Node
            ReflMetalness_Node = cmds.listConnections(i + '.refl_metalness', type='file')
            #  ReflRoughness_Node
            ReflRoughness_Node = cmds.listConnections(i + '.refl_roughness', type='file')
            # Opacity_Node
            Opacity_Node = cmds.listConnections(i + '.opacity_color', type='file')
            if ReflRoughness_Node == None:
                self.widget.EbdLog_Browser.append(" warning 没有roughness 暂时执行错误 二把刀正在完善中")
                self.widget.EbdLog_Browser.ensureCursorVisible()
                break
            if (ReflRoughness_Node != None or ReflMetalness_Node != None) and ReflRoughness_Node != ReflMetalness_Node:
                haveARMS_Node = False
            elif 'ARMS' in cmds.getAttr(ReflRoughness_Node[0] + '.computedFileTextureNamePattern'):
                haveARMS_Node = True
            else:
                haveARMS_Node = True
            if haveARMS_Node == False:

                RoughnessPath = cmds.getAttr(ReflRoughness_Node[0] + '.computedFileTextureNamePattern')

                MetallicPath = RoughnessPath.split('Roughness')[0] + 'Metallic' + RoughnessPath.split('Roughness')[-1]
                if os.path.exists(MetallicPath):
                    pass
                else:
                    MetallicPath = 0

                OpacityPath = RoughnessPath.split('Roughness')[0] + 'Opacity' + RoughnessPath.split('Roughness')[-1]
                if os.path.exists(OpacityPath):
                    pass
                else:
                    OpacityPath = 1
                AoPath = RoughnessPath.split('Roughness')[0] + 'AmbientOcclusion' + RoughnessPath.split('Roughness')[-1]
                if os.path.exists(AoPath):
                    pass
                else:
                    AoPath = 1
                ARMSPath = RoughnessPath.split('Roughness')[0] + 'ARMS' + RoughnessPath.split('Roughness')[-1]
                ARMSFilePath = ARMSPath.split('/')[0]

                ARMSName = (RoughnessPath.split('/')[-1]).split('Roughness')[0] + 'ARMS'


                if type(RoughnessPath) == str and os.path.exists(RoughnessPath):
                    Format =RoughnessPath.split('.')[-1]
                    pass
                else:
                    Format = 'jpg'
            #分类UDIM
            if '<UDIM>' in RoughnessPath:
                isUdim = True
                for b in range(1001, 1101):
                    udimRoughnessFile = RoughnessPath.split('<UDIM>')[0] + str(b) + RoughnessPath.split('<UDIM>')[-1]
                    if os.path.exists(udimRoughnessFile):
                        UDIMRoughnessPath = udimRoughnessFile
                        if type(MetallicPath) != str:
                            UDIMMetallicPath = MetallicPath
                        else:
                            UDIMMetallicPath = MetallicPath.split('<UDIM>')[0] + str(b) + MetallicPath.split('<UDIM>')[-1]
                        if type(AoPath) != str:
                            UDIMAoPath = AoPath
                        else:
                            UDIMAoPath = AoPath.split('<UDIM>')[0] + str(b) + AoPath.split('<UDIM>')[-1]
                        if type(OpacityPath) != str:
                            UDIMOpacityPath = OpacityPath
                        else:
                            UDIMOpacityPath = OpacityPath.split('<UDIM>')[0] + str(b) + OpacityPath.split('<UDIM>')[-1]
                        UDIMARMSPath = UDIMRoughnessPath.split('Roughness')[0] + 'ARMS' + UDIMRoughnessPath.split('Roughness')[-1]


                        cv2ARMS.mergeRGBA(UDIMAoPath, UDIMRoughnessPath, UDIMMetallicPath, UDIMOpacityPath,UDIMARMSPath)
                        if type(UDIMAoPath) == str and os.path.exists(UDIMAoPath):
                            shutil.copy(UDIMAoPath, backupFilePath)
                        if type(UDIMRoughnessPath) == str and os.path.exists(AoPath):
                            shutil.copy(UDIMRoughnessPath, backupFilePath)
                        if type(UDIMMetallicPath) == str and os.path.exists(UDIMRoughnessPath):
                            shutil.copy(UDIMMetallicPath, backupFilePath)
                        if type(UDIMOpacityPath) == str and os.path.exists(UDIMOpacityPath):
                            shutil.copy(UDIMOpacityPath, backupFilePath)

                # 创建ARMS_NODE
                cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=ARMSName)
                cmds.setAttr(ARMSName+ '.fileTextureName', ARMSPath,
                             type="string")
                cmds.setAttr(ARMSName + '.ignoreColorSpaceFileRules', 1)
                cmds.setAttr(ARMSName + '.colorSpace', 'Raw', type='string')
                cmds.setAttr(ARMSName + '.uvTilingMode', 3)

            else:
                isUdim = False

                print ("ARMSPath" + ARMSPath)
                cv2ARMS.mergeRGBA(AoPath, RoughnessPath, MetallicPath, OpacityPath,ARMSPath)
                if type(AoPath) == str and os.path.exists(AoPath):
                    shutil.copy(AoPath, backupFilePath)
                if type(RoughnessPath) == str and os.path.exists(RoughnessPath):
                    shutil.copy(RoughnessPath, backupFilePath)
                if type(MetallicPath) == str and os.path.exists(MetallicPath):
                    shutil.copy(MetallicPath, backupFilePath)
                if type(OpacityPath) == str and os.path.exists(OpacityPath):
                    shutil.copy(OpacityPath, backupFilePath)

                # 创建ARMS_NODE
                cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=ARMSName)
                cmds.setAttr(ARMSName + '.fileTextureName', ARMSPath, type="string")
                cmds.setAttr(ARMSName + '.ignoreColorSpaceFileRules', 1)
                cmds.setAttr(ARMSName + '.colorSpace', 'Raw', type='string')

            # 指定tex2d
            ErDTxtName = cmds.listConnections(ReflRoughness_Node[0] + '.uvCoord', type='place2dTexture')[0]
            # 链接 2dtex file链接
            UVFile = ['outUV', 'uvCoord', 'outUvFilterSize', 'uvFilterSize', 'coverage', 'coverage', 'translateFrame',
                      'translateFrame', 'rotateFrame', 'rotateFrame', 'mirrorU', 'mirrorU', 'mirrorV', 'mirrorV',
                      'stagger',
                      'stagger', 'wrapU', 'wrapU', 'wrapV', 'wrapV', ' repeatUV', 'repeatUV', 'vertexUvOne',
                      'vertexUvOne',
                      'vertexUvTwo', 'vertexUvTwo', 'vertexUvThree', 'vertexUvThree', 'vertexCameraOne',
                      'vertexCameraOne',
                      'noiseUV', 'noiseUV', 'offset', 'offset', 'rotateUV', 'rotateUV']
            aa = len(UVFile)
            UV = []
            FILE = []
            for d in range(0, aa, 2):
                UV.append(UVFile[d])
            for b in range(1, aa, 2):
                FILE.append(UVFile[b])
            bb = len(UV)
            for c in range(0, bb):
                cmds.connectAttr(ErDTxtName + '.' + UV[c], ARMSName + '.' + FILE[c])

            # 链接file到shader
            cmds.connectAttr(ARMSName + '.outColor.outColorG', i + '.refl_roughness', force=1)
            cmds.connectAttr(ARMSName + '.outColor.outColorB', i + '.refl_metalness', force=1)
            cmds.connectAttr(ARMSName + '.outAlpha', i + '.opacity_colorR', force=1)
            cmds.connectAttr(ARMSName + '.outAlpha', i + '.opacity_colorG', force=1)
            cmds.connectAttr(ARMSName + '.outAlpha', i + '.opacity_colorB', force=1)
            cmds.connectAttr(Opacity_Node[0] + '.outColor', i + '.opacity_color')
    # #循环合并RGBA
    # def LoopMergeRGBA(self):






    def SplitRGBA(self):
        sele = cmds.ls(sl=1)
        backupFilePath = cmds.workspace(fullName=True) + '/sourceimages/' + 'backupFile/'

        # 创建备份文件夹到工程目录
        if os.path.exists(backupFilePath):
            pass
        else:
            os.makedirs(backupFilePath)

        for i in sele:

            #  ReflMetalness_Node
            ReflMetalness_Node = cmds.listConnections(i + '.refl_metalness', type='file')
            #  ReflRoughness_Node
            ReflRoughness_Node = cmds.listConnections(i + '.refl_roughness', type='file')
            # ARMS_Node
            if (ReflRoughness_Node != None or ReflMetalness_Node != None) and ReflRoughness_Node == ReflMetalness_Node:
                haveARMS_Node = True
            elif 'ARMS' in cmds.getAttr(ReflRoughness_Node[0] + '.computedFileTextureNamePattern'):
                haveARMS_Node = True
            else:
                haveARMS_Node = False
            if haveARMS_Node == True:
                ARMSPath = cmds.getAttr(ReflRoughness_Node[0] + '.computedFileTextureNamePattern')
                ARMSFilePath = ARMSPath[:len(ARMSPath.split('/')[-1])*(-1)-1]
                RoughnessName = (ARMSPath.split('/')[-1]).split('ARMS')[0]+'Roughness'
                MetallicName = (ARMSPath.split('/')[-1]).split('ARMS')[0]+'Metallic'
                AoName = (ARMSPath.split('/')[-1]).split('ARMS')[0]+'AmbientOcclusion'
                OpacityName = (ARMSPath.split('/')[-1]).split('ARMS')[0]+'Opacity'
                Format = ARMSPath.split('.')[-1]

            #分类UDIM
            if '<UDIM>' in ARMSPath:
                isUdim = True
                for b in range(1001, 1101):
                    udimARMSFile = ARMSPath.split('<UDIM>')[0] + str(b) + ARMSPath.split('<UDIM>')[-1]
                    if os.path.exists(udimARMSFile):
                        RoughenessPath = udimARMSFile.split('ARMS')[0]+'Roughness'+ udimARMSFile.split('ARMS')[-1]
                        MetallicPath = udimARMSFile.split('ARMS')[0]+'Metallic'+ udimARMSFile.split('ARMS')[-1]
                        AoPath = udimARMSFile.split('ARMS')[0]+'AmbientOcclusion'+ udimARMSFile.split('ARMS')[-1]
                        OpacityPath = udimARMSFile.split('ARMS')[0]+'Opacity'+ udimARMSFile.split('ARMS')[-1]
                        cv2ARMS.splitRGBA(udimARMSFile, AoPath, RoughenessPath, MetallicPath,OpacityPath)
                        shutil.copy(udimARMSFile, backupFilePath)
                #创建RoughenessNode
                cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=RoughnessName, )
                cmds.setAttr(RoughnessName + '.fileTextureName', ARMSFilePath + '/' + RoughnessName + '_1001.' + Format,
                             type="string")
                cmds.setAttr(RoughnessName + '.ignoreColorSpaceFileRules', 1)
                cmds.setAttr(RoughnessName + '.colorSpace', 'Raw', type='string')
                cmds.setAttr(RoughnessName + '.alphaIsLuminance', 1)
                cmds.setAttr(RoughnessName + '.uvTilingMode', 3)

                #创建MetallicNode
                cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=MetallicName, )
                cmds.setAttr(MetallicName + '.fileTextureName', ARMSFilePath + '/' + MetallicName + '_1001.' + Format,
                             type="string")
                cmds.setAttr(MetallicName + '.ignoreColorSpaceFileRules', 1)
                cmds.setAttr(MetallicName + '.colorSpace', 'Raw', type='string')
                cmds.setAttr(MetallicName + '.alphaIsLuminance', 1)
                cmds.setAttr(MetallicName + '.uvTilingMode', 3)

                #创建OpacityNode
                if os.path.exists(ARMSFilePath + '/' + OpacityName + '_1001.' + Format):
                    cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=OpacityName, )
                    cmds.setAttr(OpacityName + '.fileTextureName', ARMSFilePath + '/' + OpacityName + '_1001.' + Format,
                                 type="string")
                    cmds.setAttr(OpacityName + '.ignoreColorSpaceFileRules', 1)
                    cmds.setAttr(OpacityName + '.colorSpace', 'Raw', type='string')
                    cmds.setAttr(OpacityName + '.alphaIsLuminance', 1)
                    cmds.setAttr(OpacityName + '.uvTilingMode', 3)
                else:
                    pass

                #创建AoNode
                cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=AoName, )
                cmds.setAttr(AoName + '.fileTextureName', ARMSFilePath + '/' + AoName + '_1001.' + Format,
                             type="string")
                cmds.setAttr(AoName + '.ignoreColorSpaceFileRules', 1)
                cmds.setAttr(AoName + '.colorSpace', 'Raw', type='string')
                cmds.setAttr(AoName + '.alphaIsLuminance', 1)
                cmds.setAttr(AoName + '.uvTilingMode', 3)

            else:
                isUdim = False
                RoughenessPath = ARMSPath .split('ARMS')[0] + 'Roughness' + ARMSPath .split('ARMS')[-1]
                MetallicPath = ARMSPath .split('ARMS')[0] + 'Metallic' + ARMSPath .split('ARMS')[-1]
                AoPath = ARMSPath .split('ARMS')[0] + 'Ambient occlusion' + ARMSPath .split('ARMS')[-1]
                OpacityPath = ARMSPath .split('ARMS')[0] + 'Opacity' + ARMSPath .split('ARMS')[-1]
                cv2ARMS.splitRGBA(ARMSPath , AoPath, RoughenessPath, MetallicPath, OpacityPath)
                shutil.copy(ARMSPath , backupFilePath)

                # 创建RoughenessNode
                cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=RoughnessName, )
                cmds.setAttr(RoughnessName + '.fileTextureName', RoughenessPath,
                             type="string")
                cmds.setAttr(RoughnessName + '.ignoreColorSpaceFileRules', 1)
                cmds.setAttr(RoughnessName + '.colorSpace', 'Raw', type='string')
                cmds.setAttr(RoughnessName + '.alphaIsLuminance', 1)

                # 创建MetallicNode
                cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=MetallicName, )
                cmds.setAttr(MetallicName + '.fileTextureName', MetallicPath,
                             type="string")
                cmds.setAttr(MetallicName + '.ignoreColorSpaceFileRules', 1)
                cmds.setAttr(MetallicName + '.colorSpace', 'Raw', type='string')
                cmds.setAttr(MetallicName + '.alphaIsLuminance', 1)

                # 创建OpacityNode
                if os.path.exists(ARMSPath.split('ARMS')[0]+'Opacity'+ARMSPath.split('ARMS')[-1]):
                    cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=OpacityName, )
                    cmds.setAttr(OpacityName + '.fileTextureName', OpacityPath,
                                 type="string")
                    cmds.setAttr(OpacityName + '.ignoreColorSpaceFileRules', 1)
                    cmds.setAttr(OpacityName + '.colorSpace', 'Raw', type='string')
                    cmds.setAttr(OpacityName + '.alphaIsLuminance', 1)
                else:
                    pass

                # 创建AoNode
                cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=AoName, )
                cmds.setAttr(AoName + '.fileTextureName', AoPath,
                             type="string")
                cmds.setAttr(AoName + '.ignoreColorSpaceFileRules', 1)
                cmds.setAttr(AoName + '.colorSpace', 'Raw', type='string')
                cmds.setAttr(AoName + '.alphaIsLuminance', 1)

            #指定tex2d
            ErDTxtName = cmds.listConnections(ReflRoughness_Node[0] + '.uvCoord', type='place2dTexture')[0]
            #链接 2dtex file链接
            UVFile = ['outUV', 'uvCoord', 'outUvFilterSize', 'uvFilterSize', 'coverage', 'coverage', 'translateFrame',
                      'translateFrame', 'rotateFrame', 'rotateFrame', 'mirrorU', 'mirrorU', 'mirrorV', 'mirrorV', 'stagger',
                      'stagger', 'wrapU', 'wrapU', 'wrapV', 'wrapV', ' repeatUV', 'repeatUV', 'vertexUvOne', 'vertexUvOne',
                      'vertexUvTwo', 'vertexUvTwo', 'vertexUvThree', 'vertexUvThree', 'vertexCameraOne', 'vertexCameraOne',
                      'noiseUV', 'noiseUV', 'offset', 'offset', 'rotateUV', 'rotateUV']
            aa = len(UVFile)
            UV = []
            FILE = []
            for d in range(0, aa, 2):
                UV.append(UVFile[d])
            for b in range(1, aa, 2):
                FILE.append(UVFile[b])
            bb = len(UV)
            for c in range(0, bb):
                cmds.connectAttr(ErDTxtName + '.' + UV[c], RoughnessName + '.' + FILE[c])
                cmds.connectAttr(ErDTxtName + '.' + UV[c], MetallicName + '.' + FILE[c])
                cmds.connectAttr(ErDTxtName + '.' + UV[c], AoName + '.' + FILE[c])
                if os.path.exists(ARMSPath.split('ARMS')[0]+'Opacity'+ARMSPath.split('ARMS')[-1]):
                    cmds.connectAttr(ErDTxtName + '.' + UV[c], OpacityName + '.' + FILE[c])
                else:
                    pass

            # 链接file到shader
            cmds.connectAttr(RoughnessName + '.outAlpha', i + '.refl_roughness',force = 1)
            cmds.connectAttr(MetallicName + '.outAlpha', i + '.refl_metalness',force = 1)
            if os.path.exists(ARMSPath.split('ARMS')[0] + 'Opacity' + ARMSPath.split('ARMS')[-1]):
                cmds.connectAttr(OpacityName + '.outColor', i + '.opacity_color',force = 1)
                cmds.disconnectAttr(ReflRoughness_Node[0] + '.outAlpha', i + '.opacity_colorR')
                cmds.disconnectAttr(ReflRoughness_Node[0] + '.outAlpha', i + '.opacity_colorG')
                cmds.disconnectAttr(ReflRoughness_Node[0] + '.outAlpha', i + '.opacity_colorB')
            else:
                pass

    # #循环拆分RGBA
    # def LoopSplitRGBA(self):
    #     sel = cmds.ls(sl = True,type = 'RedshiftMaterial')
    #     if len(sel) >= 1 :
    #         for i in sel:


    def SelectionMatForNormal(self):
        sel = cmds.ls(sl=1)
        select = []
        for i in sel:

            if cmds.nodeType(i) == 'RedshiftMaterial':
                RsNormal_Node = cmds.listConnections(i + '.bump_input', type='RedshiftNormalMap')
                RsBump_Node = cmds.listConnections(i + '.bump_input', type='RedshiftBumpMap')

                if RsNormal_Node != None and RsBump_Node == None:
                    select.append(i)
                else:
                    pass
            else:
                pass
        cmds.select(select)

    def ConvertNormalToBump(self):
        sel = cmds.ls(sl=1)
        for i in sel:
            if cmds.nodeType(i) != 'RedshiftMaterial':
                pass
            else:
                RsNormal_Node = cmds.listConnections(i + '.bump_input', type='RedshiftNormalMap')
                RsBump_Node = cmds.listConnections(i + '.bump_input', type='RedshiftBumpMap')
                try:
                    Judge_UDIM_Node = cmds.listConnections(i + '.diffuse_color', type='file')
                    Judge_UDIM = cmds.getAttr(Judge_UDIM_Node[0] + '.uvTilingMode')
                except:
                    Judge_UDIM_Node = cmds.listConnections(i + '.refl_roughness', type='file')
                    Judge_UDIM = cmds.getAttr(Judge_UDIM_Node[0] + '.uvTilingMode')

                udimNum = '1001'

                if RsNormal_Node == None and RsBump_Node != None:
                    pass
                elif RsNormal_Node != None and RsBump_Node == None:
                    RsNormal_Node_str = cmds.getAttr(RsNormal_Node[0] + '.tex0')
                    if '<UDIM>' in  RsNormal_Node_str:
                        RsNormal_Node_str = RsNormal_Node_str.split('<UDIM>')[0] + "1001" + RsNormal_Node_str.split('<UDIM>')[-1]

                    RsRsBump_Node_name = i + '_BumpMap'
                    RsRsBump_File_name = i + '_BumpMapFile'
                    cmds.shadingNode('file', asTexture=True, isColorManaged=True, name=RsRsBump_File_name)
                    cmds.setAttr(RsRsBump_File_name + '.fileTextureName', RsNormal_Node_str, type="string")
                    cmds.setAttr(RsRsBump_File_name + '.ignoreColorSpaceFileRules', 1)
                    cmds.setAttr(RsRsBump_File_name + '.colorSpace', 'Raw', type='string')
                    if Judge_UDIM == 3:
                        cmds.setAttr(RsRsBump_File_name + '.uvTilingMode', 3)
                    else:
                        cmds.setAttr(RsRsBump_File_name + '.uvTilingMode', 0)
                    cmds.shadingNode('RedshiftBumpMap', asTexture=True, isColorManaged=True, name=RsRsBump_Node_name, )
                    cmds.setAttr(RsRsBump_Node_name + ".inputType", 1)
                    cmds.setAttr(RsRsBump_Node_name + ".scale", 1)
                    cmds.setAttr(RsRsBump_Node_name + ".flipY", 1)
                    cmds.connectAttr(RsRsBump_File_name + '.outColor', RsRsBump_Node_name + '.input')
                cmds.connectAttr(RsRsBump_Node_name + '.out', i + '.bump_input', force=1)


            self.widget.EbdLog_Browser.append("warning 没有 对应的法线贴图节点")
            self.widget.EbdLog_Browser.ensureCursorVisible()


    #Selection

    def SelectUdimTextures(self):
        sele = cmds.ls(type="file")
        to_selected = []
        for i in sele:
            isUdim = cmds.getAttr(i + '.uvTilingMode')
            if isUdim == 3:
                to_selected.append(i)
        cmds.select(to_selected)

    def SelectNoArmsMats(self):
        sele = cmds.ls(type="RedshiftMaterial")

        NoArmsMats = []
        for i in sele:
            RoughnessNode = cmds.listConnections(i + '.refl_roughness', type='file')
            MetallicNode = cmds.listConnections(i + '.refl_metalness', type='file')
            if RoughnessNode != MetallicNode:
                NoArmsMats.append(i)
            else:
                pass
        cmds.select(NoArmsMats)

    def SimilarUdimTextures(self):
        sele = cmds.ls(type="file")
        SimilarUdim = []
        for i in sele:
            FilePath = cmds.getAttr(i + '.ftn', asString=1)
            IsUdim = cmds.getAttr(i + '.uvTilingMode')
            if IsUdim == 3:
                pass
            else:
                for a in range(1001, 1100):
                    if str(a) in FilePath:
                        SimilarUdim.append(i)
                    else:
                        pass
        cmds.select(SimilarUdim)

    def SelectAllMesh(self):
        sel = cmds.ls(type='dagNode')
        selectMesh = []
        try:
            for i in sel:
                try:
                    MeshType = cmds.nodeType(cmds.listRelatives(cmds.ls(i), shapes=True))
                    if MeshType == 'mesh':
                        selectMesh.append(i)
                    else:
                        pass
                except:
                    pass
            cmds.select(selectMesh)
        except:
            self.widget.EbdLog_Browser.append("没有包含" + i + "的file节点，请检查输入字符串后重试")
            self.widget.EbdLog_Browser.ensureCursorVisible()

    def select_TX_for_str(self):
        filter_str = self.widget.select_TX_str_lineEdit.text()
        sele = cmds.ls(type="file")
        to_selected = []
        for i in sele:
            m = re.search(filter_str, cmds.getAttr(i + '.computedFileTextureNamePattern'), re.IGNORECASE)
            if bool(m) == True:
                to_selected.append(i)
        cmds.select(to_selected)



        '''EBD 模块'''


    def select_Node_str(self):
        filter_str = self.widget.select_Node_str_lineEdit.text()
        sele = cmds.ls(type='dagNode')
        to_selected = []
        try:
            for i in sele:
                m = re.search(filter_str, i, re.IGNORECASE)
                if bool(m) == True:
                    to_selected.append(i)
            cmds.select(to_selected)
        except:
            self.widget.EbdLog_Browser.append("没有包含" + i + "的相关节点，请检查输入字符串后重试")
            self.widget.EbdLog_Browser.ensureCursorVisible()






        '''EBD 模块'''


    def GetType(self):
        if cmds.objectType(cmds.ls(sl=1)[0]) == 'transform':
            NodeType = cmds.nodeType(cmds.listRelatives(cmds.ls(selection=True,type='dagNode')[0],shapes=True))
        else:
            NodeType = cmds.objectType(cmds.ls(sl=1)[0])
        self.widget.EbdLog_Browser.append(NodeType)
        self.widget.EbdLog_Browser.ensureCursorVisible()

    def ListAttr(self):
        for i in cmds.listAttr(cmds.ls(sl=1)[0]):
            self.widget.EbdLog_Browser.append(i)
            self.widget.EbdLog_Browser.ensureCursorVisible()





    # 更新控件
    def Upadate(self):
        for i in sys.path:
            if "Ebd_Tools_Maya" in i:
                scriptPath = i.split(r'Ebd_Tools_Maya')[0]
        try:
            url = "https://codeload.github.com/dongpingyao/Ebd_Tools_Maya/zip/refs/heads/main"
        except:
            url = "http://182.92.66.60:45015/down/aV9E2zTCj2oS?fname=/ErBaDao_Tool_Maya.zip"
        filePath = scriptPath + "ebdTemp"
        fileName = filePath + r'/Ebd_Tools_Maya.zip'
        fileName2 = filePath + r'/Ebd_Tools_Maya-main.zip'
        tarfile = scriptPath
        if os.path.exists(filePath):
            shutil.rmtree(filePath)
            os.makedirs(filePath)
        else:
            os.makedirs(filePath)
        print(u"正在下载中,请稍等...")
        self.widget.EbdLog_Browser.append("正在下载中,请稍等...")
        self.widget.EbdLog_Browser.ensureCursorVisible()
        wget.download(url, filePath)
        print(u"下载完成,准备更新")
        self.widget.EbdLog_Browser.append("下载完成,准备更新")
        self.widget.EbdLog_Browser.ensureCursorVisible()


        if os.path.exists(scriptPath + r"/Ebd_Tools_Maya"):
            shutil.rmtree(scriptPath + r"/Ebd_Tools_Maya", ignore_errors=1)

            try:
                zip = zipfile.ZipFile(fileName)
            except:
                zip = zipfile.ZipFile(fileName2)
            zip.extractall(scriptPath + "ebdTemp")
            zip.close()

            if os.path.exists(scriptPath + "ebdTemp/Ebd_Tools_Maya-main"):
                os.rename(scriptPath + "ebdTemp/Ebd_Tools_Maya-main",scriptPath + "ebdTemp/Ebd_Tools_Maya")

            for root, dirs, files in os.walk(scriptPath + "ebdTemp" + r"/Ebd_Tools_Maya"):
                for file in files:
                    src_file = os.path.join(root, file).replace('\\', '/')
                    ls = src_file.split(src_file.split("/")[-1])[0][:-1]
                    target_path = ls.split("ebdTemp/")[0] + ls.split("ebdTemp/")[-1]
                    try:
                        os.makedirs(target_path)
                    except:
                        pass
                    try:
                        shutil.copy(src_file, target_path)
                    except:
                        pass
            print(u"更新完成")
            self.widget.EbdLog_Browser.append(u"更新完成")
            self.widget.EbdLog_Browser.ensureCursorVisible()

    # 跳转到主页
    @staticmethod
    def GoHome():
        web.open('http://blog.sina.com.cn/s/articlelist_2112442711_0_1.html')
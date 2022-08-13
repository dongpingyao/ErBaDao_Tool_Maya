import ErBaDao_Tool_Maya.Ebd_Tools_maya as ebd
if __name__ == "__main__":
    try:
        designer_ui.close()
        designer_ui.deleteLater()
    except:
        pass
    designer_ui = ebd.EbdToolsMaya()
    designer_ui.show()
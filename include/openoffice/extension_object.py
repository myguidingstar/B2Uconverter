"""
B2UConverter — UNO extension for OpenOffice.org
File: include/openoffice/extension_object.py

Copyright ©2009  Ministry of Science and Technology of Vietnam
License: GNU Lesser General Public License version 2.1
Authors: Jean Christophe André <jcandre@hanoilug.org>
         Lê Quốc Thái <lqthai@hanoilug.org>
         Võ Đức Phương <vdphuong@hanoilug.org>
"""

######################################################################

def B2UConverterScript(event=False):
    """Convert all document text segments from old Vietnamese encodings and fonts to Unicode encoding and fonts."""
    parser = OOoDocumentParser()
    vnConverter = VietnameseTextConverter(
        decoderPrefix='internal_',
        vniHacks=self._settings['VNIHacks'])
    oVnConverter = OOoVietnameseTextConverter(
        vnConverter,
        removeDiacritics=self._settings['RemoveDiacritics'])
    parser.setTextPortionConverter(oVnConverter)
    return parser.processDocument(XSCRIPTCONTEXT.getDocument())

g_exportedScripts = B2UConverterScript,

######################################################################

#from com.sun.star.awt import Rectangle
from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt.WindowClass import MODALTOP
from com.sun.star.awt.VclWindowPeerAttribute import OK, DEF_OK

# Show a message box with the UNO based toolkit
def messageBox(document, message):
    #doc = XSCRIPTCONTEXT.getDocument()
    window = document.CurrentController.Frame.ContainerWindow

    aDescriptor = WindowDescriptor()
    aDescriptor.Type = MODALTOP
    aDescriptor.WindowServiceName = "infobox"
    aDescriptor.ParentIndex = -1
    aDescriptor.Parent = window
    #aDescriptor.Bounds = Rectangle()
    aDescriptor.WindowAttributes = OK

    tk = window.getToolkit()
    msgbox = tk.createWindow(aDescriptor)
    msgbox.setCaptionText("Convert to Unicode")
    msgbox.setMessageText(message)

    return msgbox.execute()

######################################################################

from com.sun.star.task import XJobExecutor
from com.sun.star.beans import PropertyValue
import os
from tempfile import mkstemp
from fnmatch import fnmatch

class B2UConverterJob(unohelper.Base, XJobExecutor):
    def __init__(self, context):
        self._context = context
        self._setupLogging()
        self.parser = OOoDocumentParser()

    def _readConfig(self):
        cfgprov = self._context.ServiceManager.createInstanceWithContext(
            "com.sun.star.configuration.ConfigurationProvider", self._context)
        node = PropertyValue()
        node.Name = "nodepath"
        node.Value = "/vn.gov.oss.openoffice.B2UConverter/General"
        ConfigReader = cfgprov.createInstanceWithArguments(
            "com.sun.star.configuration.ConfigurationAccess", (node,))
        cfgnames = ("Debug", "RemoveDiacritics", "VNIHacks",
            "DebugFilename", "FolderConvertDefault", "FolderConvertPatterns")
        cfgvalues = ConfigReader.getPropertyValues(cfgnames)
        if not cfgvalues:
            raise RuntimeError, "Unable to read the configuration."
        self._settings = dict(zip(cfgnames, cfgvalues))
        loglevel = (self._settings['Debug'] and logging.DEBUG or logging.INFO)
        logging.root.setLevel(loglevel)

    def _setupLogging(self):
        self._readConfig()
        filename = self._settings.get('DebugFilename')
        if not filename: filename = '~/.B2UConverter-OOo.log'
        old_umask = os.umask(0077)
        # TODO: check if it fails and take countermesure in this case
        logging.basicConfig(
            format='%(asctime)s %(levelname)s %(message)s',
            filename=os.path.expanduser(filename),
            filemode='w')
        os.umask(old_umask)
        logging.info("B2UConverter loaded (Python %s)", sys.version)
        logging.debug("Settings: %s", self._settings)

    def _error_message(self, error_count):
        if error_count > 1:
            message = "with %s errors" % error_count
        elif error_count > 0:
            message = "with %s error" % error_count
        else:
            message = "without error"
        return message

    def convertFolder(self):
        """Recursively convert the entire folder
        by letting user select a folder to convert (file browser)
        Traverse the given folder
        """
        self._readConfig()
        folder = self.chooseFolder(self._settings['FolderConvertDefault'])
        if not folder: # User clicked on the Cancel button
            return # FIXME: uninitialized self._document causes AttributeError
        logging.debug("Converting folder: %s" % folder)

        patterns = self._settings['FolderConvertPatterns']
        if not patterns: patterns = '*.doc;*.xls;*.ppt'
        xLoader = self._context.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self._context)
        # a Desktop implements XComponentLoader interface
        self.convertDocByDoc(folder, patterns, xLoader)
        # FIXME: A summary dialog once conversion done

    def convertDocByDoc(self, folder, patterns, xLoader):
        """Traverse a folder and convert all supported documents (ODT, ODP, etc.)
        Apply filtering to all files retrieved
        Convert each document, save & close
        """
        loadProp = PropertyValue()
        loadProp.Name = "Hidden"
        loadProp.Value = True

        for path in self.findFiles(folder, patterns):
            url = unohelper.systemPathToFileUrl(path)
            doc = xLoader.loadComponentFromURL(url, "_blank", 0, (loadProp,))
            self.convertDocument(doc)
            # It's wiser choice to save & close one document
            # at once before processing the next
            try:
                doc.store()
            finally:
                # XXX: this could generate an exception too
                try:
                    doc.close(True)
                except:
                    logging.exception("Exception when closing document '%s'",
                                                                        url)

    def findFiles(self, root, patterns='*'):
        """
        Recursively get all supported documents (text, slides, spreadsheet)
        under a given folder (param 'root')
        """
        # Expand patterns from semicolon-separated string to list
        patterns = patterns.split(';')
        for path, subdirs, files in os.walk(root):
            #files.sort( )
            for name in files:
                # TODO: apply a file pattern to filter supported document formats
                for pattern in patterns:
                    if fnmatch(name, pattern):
                        yield os.path.join(path, name)
                        break

    def chooseFolder(self, folder="~/B2UConverter"):
        folder = unohelper.systemPathToFileUrl(os.path.expanduser(folder))
        folderPicker = self._context.ServiceManager.createInstanceWithContext(
            "com.sun.star.ui.dialogs.FolderPicker", self._context)
        folderPicker.setDisplayDirectory(folder)
        if folderPicker.execute():
            selectedFolder = folderPicker.getDirectory()
            selectedFolder = unohelper.fileUrlToSystemPath(selectedFolder)
        else:
            selectedFolder = None # Cancel button pressed
        return selectedFolder

    def convertDocument(self, document=None):
        logging.debug("call to convertDocument (%s document)" \
                                % (document and "with" or "without"))
        if document:
            self._document = document
        else:
            desktop = self._context.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self._context)
            self._document = desktop.getCurrentComponent()

        self._readConfig()
        vnConverter = VietnameseTextConverter(
            decoderPrefix='internal_',
            vniHacks=self._settings['VNIHacks'])
        oVnConverter = OOoVietnameseTextConverter(
            vnConverter,
            removeDiacritics=self._settings['RemoveDiacritics'])
        self.parser.setTextPortionConverter(oVnConverter)
        self.parser.processDocument(self._document)
        logging.info("Conversion completed (%s).",
                        self._error_message(self.parser.stats['errors']))

    def convertClipboard(self):
        self._readConfig()
        logging.debug("call to convertClipboard")
        desktop = self._context.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self._context)
        clipboard = self._context.ServiceManager.createInstanceWithContext(
            "com.sun.star.datatransfer.clipboard.SystemClipboard",
            self._context)
        self._document = desktop.getCurrentComponent()

        # Get the contents from the clipboard, try to extract the data using
        # OpenOffice XML flavor
        # TODO: Adding support for more flavors like richtext or plaintext
        contents = clipboard.getContents()
        flavors = contents.getTransferDataFlavors()
        logging.debug("Clipboard flavors:\n%s",
                "* " + "\n* ".join([flavor.MimeType for flavor in flavors]))
        mimetype = 'application/x-openoffice-embed-source-xml' \
                    ';windows_formatname="Star Embed Source (XML)"'
        found_flavor = None
        for flavor in flavors:
            if flavor.MimeType == mimetype:
                found_flavor = flavor
                break

        # FIXME: No suitable flavor found, warn user that nothing has been
        # converted
        # if found_flavor == None:
        data = contents.getTransferData(found_flavor)

        # Okay, since OO.o APIs only accept an URL, we have to make a temp file
        # in order to use it.
        tempFile,path = mkstemp()
        os.write(tempFile, data.value)
        tempURL = unohelper.systemPathToFileUrl(path)

        # Open it hiddenly
        hidden = PropertyValue()
        hidden.Name = "Hidden"
        hidden.Value = True
        document = desktop.loadComponentFromURL(tempURL, "_blank", 0,
                (hidden,))

        # Let process it
        # TODO: Improve encoding detection so we can convert even if the
        # supplied font information is incorrect.
        vnConverter = VietnameseTextConverter(
            decoderPrefix='internal_',
            vniHacks=self._settings['VNIHacks'])
        oVnConverter = OOoVietnameseTextConverter(
            vnConverter,
            removeDiacritics=self._settings['RemoveDiacritics'])
        self.parser.setTextPortionConverter(oVnConverter)
        self.parser.processDocument(document)

        # Ok, now to put it back in the clipboard
        dispatcher = self._context.ServiceManager.createInstanceWithContext(
                        "com.sun.star.frame.DispatchHelper", self._context)
        frame = document.getCurrentController().getFrame()
        dispatcher.executeDispatch(frame, ".uno:SelectAll", "", 0, ())
        dispatcher.executeDispatch(frame, ".uno:Copy", "", 0, ())

        # Some clean ups
        os.close(tempFile)

    def convertSelection(self):
        pass

    def trigger(self, args):
        logging.debug("Trigger arguments: %s", args)
        try:
            if args == 'document':
                self.convertDocument()
            elif args == 'clipboard':
                self.convertClipboard()
            elif args == 'selection':
                self.convertSelection()
            elif args == 'folder':
                self.convertFolder()
            else:
                raise ValueError, "Invalid trigger call (programming error)."
            messageBox(self._document, "Unicode conversion completed (%s)." \
                        % self._error_message(self.parser.stats['errors']))
        except:
            logging.exception("Exception during conversion:")
            err = traceback.format_exc()
            try:
                import re
                err = re.sub('File "([^"]*/)+','File ".../', err)
            except:
                pass
            messageBox(self._document, "Unicode conversion failed:\n\n" + err)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation( \
    B2UConverterJob, "vn.gov.oss.openoffice.B2UConverterJob", \
    ("com.sun.star.task.Job",),)

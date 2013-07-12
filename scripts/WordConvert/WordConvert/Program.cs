using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using Microsoft.Office.Interop.Word;
using Microsoft.Office.Interop;

namespace WordConvert
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        /// 
        [System.Runtime.InteropServices.DllImport("kernel32.dll")]
        private static extern bool AllocConsole();

        [System.Runtime.InteropServices.DllImport("kernel32.dll")]
        private static extern bool AttachConsole(int pid);

        [STAThread]
        static void Main(string[] args)
        {
            /*System.Windows.Forms.Application.EnableVisualStyles();
            System.Windows.Forms.Application.SetCompatibleTextRenderingDefault(false);
            System.Windows.Forms.Application.Run(new Form1());*/

            if (!AttachConsole(-1))
            { // Attach to an parent process console
                AllocConsole(); // Alloc a new console
            }

            if (args.Length != 1)
            {
                ShowUsage();
                return;
            }

            string path = args[0].Replace("\"", @"\");
            Console.WriteLine("Convering all files under " + path);
            

//            foreach (object fileName in Directory.EnumerateFiles(@"C:\Users\d\Documents\My Dropbox\perry\bootstrap learning\t\", "*.doc", SearchOption.AllDirectories))
            foreach (object fileName in Directory.EnumerateFiles(path, "*.doc", SearchOption.AllDirectories))
            {
                Console.WriteLine("Processing " + fileName);
                ProcessDocument(fileName);
            }

        }

        static void ShowUsage()
        {
            Console.WriteLine();
            Console.WriteLine("Usage: WordConvert [Parent Directory]");
            Console.WriteLine();
            Console.ReadKey();
        }
        private static void addLinkToBookmark(Range rng, _Document doc){
            object missing = System.Reflection.Missing.Value;
            string[] matchedText = rng.Text.Split(' ');
            string pageNum;
            pageNum = matchedText[matchedText.Length - 1];
            doc.Hyperlinks.Add(rng, missing, "bkmPage" + pageNum, missing, missing, missing);
            rng.Find.Execute(
             ref missing, ref missing, ref missing, ref missing, ref missing,
             ref missing, ref missing, ref missing, ref missing, ref missing,
             ref missing, ref missing, ref missing, ref missing, ref missing);
        }

        private static void addAllLinks(_Document doc){
            Range rng = doc.Content;
            Find f = rng.Find;
            object oTrue = true;
            object missing = System.Reflection.Missing.Value;
            rng.Find.ClearFormatting();
            rng.Find.Text = "[Ss]lide @[0-9]@>";
            rng.Find.MatchWildcards = true;
            rng.Find.Execute(
             ref missing, ref missing, ref missing, ref missing, ref missing,
             ref missing, ref missing, ref missing, ref missing, ref missing,
             ref missing, ref missing, ref missing, ref missing, ref missing);
            do
            {
                addLinkToBookmark(rng, doc);
                rng.Find.Execute(
                 ref missing, ref missing, ref missing, ref missing, ref missing,
                 ref missing, ref missing, ref missing, ref missing, ref missing,
                 ref missing, ref missing, ref missing, ref missing, ref missing);
//                Console.WriteLine(rng.Text.ToString());
            } while (rng.Find.Found);
        }
        private static void addBookmarkToEveryPage(_Application wdApp, _Document doc) {

            object unitWdStory = WdUnits.wdStory;
            object oFalse = false;
            object pageBkm = "\\Page";
            object gotoWdGoToPage = WdGoToItem.wdGoToPage;
            object gotoWdGoToNext = WdGoToDirection.wdGoToNext;
            object gotoCount1 = 1;
            object oCollapseStart = WdCollapseDirection.wdCollapseStart;
            object missing = System.Reflection.Missing.Value;

            Selection sel = wdApp.Selection;
            sel.HomeKey(ref unitWdStory, ref oFalse); //Start of doc
            //Assign entire page to range
            Range rngPage = sel.Bookmarks.get_Item(ref pageBkm).Range;
            //We need a second, independent object so that we can later
            //compare the two objects
            Range rngBkm = rngPage.Duplicate;
            //Collapse the second object to a point
            //(will be bookmark location, at top of page)
            rngBkm.Collapse(ref oCollapseStart);
            int counter = 0;
            int lNumPages = (int)sel.get_Information(WdInformation.wdNumberOfPagesInDocument);
            string pageNr = null;

            //Execute at least once, 
            //then as long as the last bookmark isn't on the page with the cursor
            // (when can't go to next page, not error occurs, selection stays on last page)
            while (counter == 0 || !rngBkm.InRange(rngPage))
            {
                counter++;
                rngPage.Collapse(ref oCollapseStart);
                //Extra security against an infinite loop
                if (counter > lNumPages) break;
                //Determine the page number
                pageNr = sel.get_Information(WdInformation.wdActiveEndPageNumber).ToString();
                rngBkm = rngPage.Duplicate;
                object oRngBkm = rngBkm;
                //Add a bookmark
                rngPage.Bookmarks.Add("bkmPage" + pageNr, ref oRngBkm);
                //Go to the next page
                sel.GoTo(ref gotoWdGoToPage, ref gotoWdGoToNext, ref gotoCount1, ref missing);
                //Get the full page, for the comparison at the top of the loop
                rngPage = sel.Bookmarks.get_Item(ref pageBkm).Range;
            }        
        }
        private static void saveAsPDF(object sourceDocPath, string targetFilePath){
/*            // Make sure the source document exists.
            if (!System.IO.File.Exists(sourceDocPath))
                throw new Exception("The specified source document does not exist.");*/

            // Create an instance of the Word ApplicationClass object.          
            _Application wordApplication = new Microsoft.Office.Interop.Word.Application();
            Document wordDocument = null;

            // Declare variables for the Documents.Open and ApplicationClass.Quit method parameters. 
            object paramSourceDocPath = sourceDocPath;
            object paramMissing = Type.Missing;

            // Declare variables for the Document.ExportAsFixedFormat method parameters.
            string paramExportFilePath = targetFilePath;
            WdExportFormat paramExportFormat = WdExportFormat.wdExportFormatPDF;
            bool paramOpenAfterExport = false;
            WdExportOptimizeFor paramExportOptimizeFor = WdExportOptimizeFor.wdExportOptimizeForOnScreen;
            WdExportRange paramExportRange = WdExportRange.wdExportAllDocument;
            int paramStartPage = 0;
            int paramEndPage = 0;
            WdExportItem paramExportItem = WdExportItem.wdExportDocumentContent;
            bool paramIncludeDocProps = true;
            bool paramKeepIRM = true;
            WdExportCreateBookmarks paramCreateBookmarks =
                WdExportCreateBookmarks.wdExportCreateWordBookmarks;
            bool paramDocStructureTags = true;
            bool paramBitmapMissingFonts = true;
            bool paramUseISO19005_1 = false;

            try
            {
                // Open the source document.
                wordDocument = wordApplication.Documents.Open(ref paramSourceDocPath, ref paramMissing, ref paramMissing, ref paramMissing,
                    ref paramMissing, ref paramMissing, ref paramMissing, ref paramMissing, ref paramMissing, ref paramMissing,
                    ref paramMissing, ref paramMissing, ref paramMissing, ref paramMissing, ref paramMissing, ref paramMissing);

                // Export it in the specified format.
                if (wordDocument != null)
                    wordDocument.ExportAsFixedFormat(paramExportFilePath, paramExportFormat, paramOpenAfterExport, paramExportOptimizeFor,
                        paramExportRange, paramStartPage, paramEndPage, paramExportItem, paramIncludeDocProps, paramKeepIRM, paramCreateBookmarks, paramDocStructureTags,
                        paramBitmapMissingFonts, paramUseISO19005_1, ref paramMissing);
            }
            catch (Exception e)
            {
                throw e;
            }
            finally
            {
                // Close and release the Document object.
                if (wordDocument != null)
                {
                    wordDocument.Close(ref paramMissing, ref paramMissing, ref paramMissing);
                    wordDocument = null;
                }

                // Quit Word and release the ApplicationClass object.
                if (wordApplication != null)
                {
                    wordApplication.Quit(ref paramMissing, ref paramMissing, ref paramMissing);
                    wordApplication = null;
                }

                GC.Collect();
                GC.WaitForPendingFinalizers();
                GC.Collect();
                GC.WaitForPendingFinalizers();
            }
        }
        private static void ProcessDocument(object fileName)
        {
            
            object missing = System.Reflection.Missing.Value;

            _Application wdApp;
            wdApp = new Microsoft.Office.Interop.Word.Application();
            _Document doc;

            doc = wdApp.Documents.Open(ref fileName,
                ref missing, ref missing, ref missing, ref missing, ref missing,
                ref missing, ref missing, ref missing, ref missing, ref missing,
                ref missing, ref missing, ref missing, ref missing, ref missing);


            addBookmarkToEveryPage(wdApp, doc);
            addAllLinks(doc);

            string newFileName = Path.ChangeExtension(Convert.ToString(fileName), "PDF");
//            System.Console.WriteLine(newFileName);

            doc.Close(WdSaveOptions.wdSaveChanges);
            doc = null;

            GC.Collect();
            GC.WaitForPendingFinalizers();

            saveAsPDF(fileName, newFileName);

            wdApp.Quit();
            wdApp = null;


            GC.Collect();
            GC.WaitForPendingFinalizers();
        }


 
    }
}

//Hey Bobby, sorry this is such a POS :-). Let me know if some part of it is incomprehensible and I'll do some refactoring to clean things up

#if INTERACTIVE
    #r "Microsoft.Office.Interop.Excel"
    #r "System.Windows.Forms"
    #r "System.Windows.Presentation"
    #r "System.Xaml"
#endif

open System.IO
open System.Diagnostics
open System.Reflection
open Microsoft.Office.Interop.Excel
open System.Text
open System
open System.Text.RegularExpressions
open System.Windows
open System.Windows.Controls
open System.Windows.Markup
open System.Xml
open System.Linq

//return a sequence of all files under a subdirectory
let rec filesUnder basePath =
    if Directory.Exists basePath then //we won't have a logs dir if the person quits before taking any tests
        seq {
            yield! Directory.GetFiles(basePath)
            for subDir in Directory.GetDirectories(basePath) do
                yield! filesUnder subDir 
        }
    else
//        Console.WriteLine ("WARNING: " + basePath + " not found")
        Seq.empty

//return a sequence of all directories under a subdirectory
let rec dirsUnder basePath =
    seq {
        yield! Directory.GetDirectories(basePath)
        for subDir in Directory.GetDirectories(basePath) do
            yield! dirsUnder subDir 
    }


//execute a shell command with lots of options that we never use. It was useful to have the options while debugging, but there's no need for this function to be this complicated now.
let shellExecute program arguments dir =
    let startInfo = new ProcessStartInfo()
    startInfo.FileName  <- program
    startInfo.Arguments <- arguments
    
    startInfo.UseShellExecute        <- false
    startInfo.RedirectStandardOutput <- true
    startInfo.WorkingDirectory <- dir

    let proc = new Process()
    proc.EnableRaisingEvents <- true
    
    // Add a handler to the 'OutputDataRecieved' event, so we can store
    // the STDOUT stream of the process.
    let driverOutput = new StringBuilder()        
    proc.OutputDataReceived.AddHandler(DataReceivedEventHandler((fun sender args -> driverOutput.AppendLine(args.Data) |> ignore)))
    
    proc.StartInfo <- startInfo
    proc.Start() |> ignore
    proc.BeginOutputReadLine()
    
    proc.WaitForExit()
    (proc.ExitCode, driverOutput.ToString())

//in terms of the grading doc, everything is offset by 1, e.g., 0 here is 1 in the grading doc.
let errorsToIdx = Map ["Antenna_Motion_Error", 0; 
        "Baseband_Misconfiguration", 1; 
        "Antenna_Intrack_Pointing_Error",2;
        "Antenna_Azimuth_Pointing_Error",3;
        "Antenna_Elevation_Pointing_Error",4;
        "Baseband_Hangup",5;
        "None", 6]

//grade all files under a directory (including all subdirectories)
let gradeFiles (resultMap : Map<string,string>) testSimDir runGradingScript baseDir =
    let logsDir = testSimDir + "logs"
    let gradeCommand logFileName = @"-cp " + "\"" + baseDir + "HiddenDomainSimulator.jar\" com.stottlerhenke.blearn.gs.ui.XmlGrader " + "\"" + logFileName + "\""

    if runGradingScript then
        let logFileNames = filesUnder logsDir |> Seq.filter(fun filePath -> filePath.ToUpper().EndsWith("XML")) |> Seq.sort //need to sort to match the order of test names in gsTests
        logFileNames |> Seq.iter(fun fileName -> shellExecute "java" (gradeCommand fileName) testSimDir |> ignore)

    let resultFileNames = filesUnder logsDir |> Seq.filter(fun filePath -> filePath.ToUpper().EndsWith("TXT")) |> Seq.sort
    let passedTest = resultFileNames 
                        |> Seq.map(fun fileName -> File.ReadAllText fileName) 
                        |> Seq.map(fun result -> Regex.Match(result,"- (.*)").Groups.Item(1).Value.Trim())
                        |> Seq.map(fun result -> resultMap.[result])
                        |> Seq.toList
    passedTest
   

//takes a "test_simulator" directory, and runs gradeFileFun on it to generate a set of passees and fails
//Also 'backtracks' to find quiz grades and metadata associated with that run
let gradeTestDir gradeFileFun runGradingScript baseDir testDir  =
    let testSimDir = testDir + @"\"
    let finalTestSimDir = testSimDir + @"..\final_simulator\"
    let preTestSimDir = testSimDir + @"..\pretest_simulator\"
    let penultimateTestSimDir = testSimDir + @"..\penultimate_simulator\"
    let metaDataPath = testSimDir + @"..\metadata.log"

    let getMetaData metaDataPath =
        try
            let metaData = File.ReadAllText metaDataPath
            let studyRev = Regex.Match(metaData,"\"study_revision\":\s*(\d+)").Groups.Item(1).Value
            let testTime = Regex.Match(metaData,"\"test_time\":\s*(\d+)").Groups.Item(1).Value
            let noQuizFeedback = Regex.Match(metaData,"\"no_quiz_feedback\":\s*(\w+)").Groups.Item(1).Value
            (studyRev,testTime,noQuizFeedback)
        with 
            | :? System.IO.FileNotFoundException -> ("","","")

    let getSingleQuizScores quizLogPath = 
        let quizLog = File.ReadAllText quizLogPath

        let getScores txt = [for m in Regex.Matches(txt,"\"score\":\s*(\d+\.?\d*)") -> m.Groups.Item(1).Value + "%"]
        let singleQuizScores = Array.create 2 ""
        getScores quizLog |> List.iteri (fun i score -> singleQuizScores.[i] <- score)
        String.Join(",",singleQuizScores)

    let getSingleGrade (grades : string list) = match grades with
        | [] -> ""
        | lst -> lst |> List.rev |> List.head

    let getNimString() =
        let htmlFilePath = testSimDir + @"..\ASB_Study.htm"
        let htmlContent = File.ReadAllText htmlFilePath
        let getNims txt = [for m in Regex.Matches(txt,"Misconfigured_(\S+)_slides") -> m.Groups.Item(1).Value] |> List.toSeq |> Seq.distinct |> Seq.map (fun s -> Regex.Replace(s, "BF", "F"))|> Seq.toArray
        let nims = String.Join(" ",htmlContent |> getNims)
        nims

    //FIXME: kludge to fix alignment if quizzes are skipped
    let padQuizString (quizString : string) =
       quizString + String.replicate (9 - quizString.Count(fun c -> ','.Equals c)) ","

    let quizLogDir = testSimDir + @"..\quizzes\"
    let allQuizLogPaths = filesUnder quizLogDir |> Seq.filter (fun dir -> dir.EndsWith(@".log")) |> Seq.sort
    let allQuizScores = String.Join(",", allQuizLogPaths |> Seq.map getSingleQuizScores) |> padQuizString

    let studyRev,testTime,noQuizFeedback = getMetaData metaDataPath
    let nims = getNimString()

    //blah! refactor!
    let gsTests = testSimDir + "gsTests.txt"
    let preGsTests = preTestSimDir + "gsTests.txt"
    let resultMap = Map ["Passed","1";"Failed","0";@"Failed -- Connection good at end, just not fixed quickly enough; may not have received/fixed second half of intrack error",".49";"Failed -- Connection good at end, just not fixed quickly enough",".5";@"Failed -- Initially fixed error in time, but not good connection at end",".51";@"Failed -- Failed to get multi-fault scenario working","0";@"Passed -- Multi-fault working at end","1"]

    let getTestNames txt = [for m in Regex.Matches(txt,"\d=(\S+)") -> m.Groups.Item(1).Value]
    let testNames = File.ReadAllText gsTests |> getTestNames //fault condition being tested
    let preTestName = (File.ReadAllText preGsTests |> getTestNames).[0]

    //blah! refactor!
    let passedTests = gradeFileFun resultMap testSimDir runGradingScript baseDir
    let passedPreTest = gradeFileFun resultMap preTestSimDir runGradingScript baseDir |> getSingleGrade
    let passedFinalTest = gradeFileFun resultMap finalTestSimDir runGradingScript baseDir |> getSingleGrade
    let passedPenultimateTest = gradeFileFun resultMap penultimateTestSimDir runGradingScript baseDir |> getSingleGrade

    let indexedResults = Array.create errorsToIdx.Count ""

    let testOrder = String.Join("",testNames |> List.map (fun n -> errorsToIdx.[n] + 1 |> string))
    assert (testOrder.Length = 5)

    try
        List.iter2 (fun p n -> indexedResults.[errorsToIdx.[n]] <- p) passedTests testNames
    with
        | :? System.ArgumentException -> Console.WriteLine ("WARNING: " + testDir + " didn't take all tests") //catch length mismatch, which happens when subject leaves before taking all tests

    let preTestIdx = errorsToIdx.[preTestName] + 1 |> string

    //FIXME: returning this tuple is completely ridiculous
    (indexedResults,testOrder,preTestIdx,passedPreTest,passedPenultimateTest,passedFinalTest,nims,allQuizScores,studyRev,testTime,noQuizFeedback)


//pop up an excel spreadsheet showing all the results
let outputToExcel results header =
    let app = ApplicationClass(Visible = true)

    let sheet = app.Workbooks.Add().Worksheets.[1] :?> _Worksheet

    let setCellText (x : int) (y : int) (text : string) =
        //this kludge really needs to be fixed. We're assuming we never go past 'AZ'
        let range =
            if (x + int 'A') <= (int 'Z') then
                sprintf "%c%d" (char (x + int 'A')) (y+1)
            else
                sprintf "A%c%d" (char (x + int 'A' - 26)) (y+1)        
        sheet.Range(range).Value(Missing.Value) <- text
    let printCsvToExcel rowIdx (csvText : string) = csvText.Split([| ',' |]) |> Array.iteri (fun partIdx partText -> setCellText partIdx rowIdx partText)

    printCsvToExcel 0 header
    results |> Seq.iteri (fun i str -> printCsvToExcel (i+1) str)

let outputToCSV outFileName results header = 
    File.WriteAllText(outFileName, header)
    File.AppendAllLines(outFileName,[|"\n"|]) //AppendAllLines seems to ignore trailing whitespace; adding this avoids cramming crap onto the header line
    File.AppendAllLines(outFileName,results |> Seq.toArray)

let gradeAllAndOutput excelOutput csvOutput runGradingScript baseDir = 
    let outFileName = baseDir + "results2.txt"

    let allTestDirs = dirsUnder baseDir |> Seq.filter (fun dir -> dir.EndsWith(@"\test_simulator"))

    //calls the gradeTestDir function on all matching directories
    let getResults gradeTestDirFun = allTestDirs |> Seq.map(fun dir -> 
        let runNum = Regex.Match(dir,"Run(\d+)").Groups.Item(1).Value
        let stationNum = Regex.Match(dir,"station_(\d+)").Groups.Item(1).Value
        let (indexedResults : string [] ),testOrder,preTestIdx,passedPreTest,passedPenultimateTest,passedFinalTest,nims,allQuizScores,studyRev,testTime,noQuizFeedback = gradeTestDirFun dir
        //wow. Should have really used sprintf here
        let resultString = runNum + "_" + stationNum + ",," + nims + ",,,," + studyRev + ",,," + preTestIdx + "," + passedPreTest + "," + allQuizScores + "," + testOrder + "," + String.Join(",",indexedResults) + ",," + passedPenultimateTest + "," + passedFinalTest + "," + testTime + "," + noQuizFeedback + ","
        Console.WriteLine resultString
        resultString)

    let results = getResults (gradeTestDir gradeFiles runGradingScript baseDir)

    let errorNames = errorsToIdx |> Map.toArray |> Array.sortBy snd |> Array.map fst |> Array.map (fun s -> Regex.Replace(s, "_|Error", " "))
//    let header = "Subject ID," + String.Join(",",errorNames) +  ",Test Order,Pre-Test Condition, Pre-Test Score,Antenna Intrack Pointing 2,Multi-fault,NIMs \n"
    //this new header was taken directly from subject-data-summary.xls
    let header = @"Subject ID,Notes,NIM Cond.,Classification,Major,Date,Study Version,Start Time,End Time,Pre-test,,Quiz Scores,,,,,,,,,,Post-test Order,Post-Test-1,,,,,,,,Post-Test-2,Final-Test,Test Time, Hidden Quiz Feedback"

    if csvOutput then
        outputToCSV outFileName results header

    if excelOutput then
        outputToExcel results header

    System.Console.ReadKey() |> ignore

// gradeAllAndOutput excelOutput csvOutput |> ignore

let createWindow (file : string) =
    using (XmlReader.Create(file)) (fun stream ->
        (XamlReader.Load(stream) :?> Window))
        
// create the window object and add event handler
// to the button control
let window =
    let temp = createWindow "../../Window1.xaml"
    let press = temp.FindName("press") :?> Button
    let textbox = temp.FindName("input") :?> TextBox
    let label = temp.FindName("output") :?> Label
    let rg = temp.FindName("run_grading") :?> CheckBox
    let eo = temp.FindName("excel_output") :?> CheckBox
    let csv = temp.FindName("csv") :?> CheckBox
    
//    press.Click.Add (fun _ -> label.Content <- textbox.Text )
    press.Click.Add (fun _ -> gradeAllAndOutput eo.IsChecked.Value csv.IsChecked.Value rg.IsChecked.Value textbox.Text)
    temp
    
// run the application
let main() =
    let app = new Application()
    app.Run(window) |> ignore
    
[<STAThread>]
do main()

//TODO: don't hardcode base directory
//TODO: replace most arrays with sequences. It's much more natural, and would also be more efficient
//TODO: pre/final/penultimate test stuff should be refactored into single function
//TODO: refactor get* txt functions into single function
//TODO: replace regexes with JSON parser
//TODO: refactor regex extraction, since we always use Groups.Item(1).Value
//TODO: get rid of pointless use of arrays
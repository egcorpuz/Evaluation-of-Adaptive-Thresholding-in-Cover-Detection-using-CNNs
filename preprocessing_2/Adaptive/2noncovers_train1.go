package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"os/signal"
	"path"
	"strings"
	"sync"
	"syscall"
)

// configuration constants
const (
	inputDir  = "./3_train_adaptive"
	OutDir    = "5_train_noncovers_img_adaptive"
	songLimit = 32131 //
	fileLimit = 32131 //should be equal
	procCount = 20
)

type counter struct {
	fileCount int
	songCount int
	mu        sync.Mutex
}

var fileCount int
var folderCount int

func IOReadDir(root string) ([]string, error) {
	var files []string
	fileInfo, err := ioutil.ReadDir(root)
	if err != nil {
		return files, err
	}

	for _, file := range fileInfo {
		files = append(files, file.Name())
	}
	return files, nil
}

func main() {
	os.Mkdir(OutDir, 0755)

	files, err := IOReadDir(inputDir)
	if err != nil {
		fmt.Printf("Error: %v", err)
		return
	}

	c := make(chan [2]*exec.Cmd, 100)
	stop := make(chan bool)
	killChan := make(chan os.Signal)
	signal.Notify(killChan, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-killChan
		fmt.Println("\r- Ctrl+C pressed in Terminal")
		stop <- true
		close(stop)
	}()

	fileCount = 0
	folderCount = 0
	go func() {
		defer close(c)
		for i, refFolder := range files {
			for _, queryFolder := range files[i+1:] {
				fmt.Printf("Cross similarity: reference folder '%v', query folder: '%v'\n", refFolder, queryFolder)
				refDir := path.Join(inputDir, refFolder)
				queryDir := path.Join(inputDir, queryFolder)
				crossSimilarity(stop, c, refDir, queryDir)
				folderCount++
				if fileCount == fileLimit {
					return
				}

				if folderCount >= songLimit {
					return
				}
			}
		}
	}()

	var wg sync.WaitGroup

	for i := 1; i <= procCount; i++ {
		wg.Add(1)

		go func(id int) {
			defer wg.Done()
			for cmd := range c {
				fmt.Printf("GOROUTINE %d: Executing %v\n", id, cmd[0])
				err := cmd[0].Run()
				if err != nil {
					fmt.Printf("GOROUTINE %d ERROR: %v\n", id, err)
				}

				fmt.Printf("GOROUTINE %d: Executing %v\n", id, cmd[1])
				err = cmd[1].Run()
				if err != nil {
					fmt.Printf("GOROUTINE %d ERROR: %v\n", id, err)
				}
				strCmd := fmt.Sprintf("%v", cmd[1])
				err = os.Remove(strings.Split(strCmd, " ")[1])
				if err != nil {
					fmt.Printf("GOROUTINE %d ERROR: %v\n", id, err)
				}

			}

		}(i)
	}
	wg.Wait()

	fmt.Printf("Done processing %d folder pairs, %d files.\n", folderCount, fileCount)
}

func crossSimilarity(stop chan bool, c chan [2]*exec.Cmd, refDir string, queryDir string) {
	refFiles, err := IOReadDir(refDir)
	if err != nil {
		fmt.Printf("Error: %v", err)
		return
	}

	queryFiles, err := IOReadDir(queryDir)
	if err != nil {
		fmt.Printf("Error: %v", err)
		return
	}
	refFile := refFiles[0]
	queryFile := queryFiles[0]
	fmt.Printf("Processing reference file: '%v', query file: '%v'\n", refFile, queryFile)
	refFileDir := path.Join(refDir, refFile)
	queryFileDir := path.Join(queryDir, queryFile)

	outputFile := fmt.Sprintf("%v-%v.csv", strings.TrimRight(refFile, ".csv"),
		strings.TrimRight(queryFile, ".csv"))
	outputDir := path.Join(OutDir, outputFile)
	jpgOutputDir := fmt.Sprintf("%v.jpg", strings.TrimRight(outputDir, ".csv")) // %v-r if reversed
	// check if jpg already exists
	if _, err := os.Stat(jpgOutputDir); err == nil {
		fmt.Printf("Output file '%v' already processed.\n", outputFile)
		fileCount++
		return
	}
	csvCommand := exec.Command("./crosssimilarity.py", refFileDir, queryFileDir, outputDir) // crosssimilarity2 for reversed
	jpgCommand := exec.Command("./csvtojpg.py", outputDir, jpgOutputDir)
	commands := [2]*exec.Cmd{
		csvCommand,
		jpgCommand,
	}
	if fileCount == fileLimit {
		return
	} else {
		c <- commands
		fileCount++
	}
}

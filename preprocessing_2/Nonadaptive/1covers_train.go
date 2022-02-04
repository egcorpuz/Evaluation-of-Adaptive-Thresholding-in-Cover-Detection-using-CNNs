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
	inputDir  = "./2_train_clipped"
	OutDir    = "5_train_covers_img"
	songLimit = 254 // total folders
	fileLimit = 2350  // limit of pairs
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
		for _, refFolder := range files {
			fmt.Printf("Cross similarity: reference folder '%v'\n", refFolder)
			refDir := path.Join(inputDir, refFolder)
			crossSimilarity(stop, c, refDir)
			folderCount++
			if fileCount == fileLimit {
				return
			}
			if folderCount >= songLimit {
				return
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

func crossSimilarity(stop chan bool, c chan [2]*exec.Cmd, refDir string) {
	refFiles, err := IOReadDir(refDir)
	if err != nil {
		fmt.Printf("Error: %v", err)
		return
	}

	for i, refFile := range refFiles {
		for _, queryFile := range refFiles[i+1:] {
			fmt.Printf("Processing reference file: '%v', query file: '%v'\n", refFile, queryFile)
			refFileDir := path.Join(refDir, refFile)
			queryFileDir := path.Join(refDir, queryFile)

			outputFile := fmt.Sprintf("%v-%v.csv", strings.TrimRight(refFile, ".csv"),
				strings.TrimRight(queryFile, ".csv"))
			outputDir := path.Join(OutDir, outputFile)
			jpgOutputDir := fmt.Sprintf("%v.jpg", strings.TrimRight(outputDir, ".csv")) // %v-r.jpg if reverse 
			// check if jpg already exists
			if _, err := os.Stat(jpgOutputDir); err == nil {
				fmt.Printf("Output file '%v' already processed.\n", outputFile)
				fileCount++
				continue
			}
			csvCommand := exec.Command("./crosssimilarity.py", refFileDir, queryFileDir, outputDir) // crosssimilarity2.py if reversed
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
	}
}

package main

import (
  "net/http"
  "fmt"
  "io/ioutil"
  "encoding/json"
  "strings"
)

var _ = strings.Fields

func errorify(err error) {
  if err != nil {
    fmt.Printf("%s", err)
    panic(err)
  }
}



func fetch(address string) (wordData interface{}) {
  resp, err := http.Get(address)
  errorify(err)
  contents, err := ioutil.ReadAll(resp.Body)
  errorify(err)
  // res := string(contents)
  
  err = json.Unmarshal(contents, &wordData)
  errorify(err)
  
  return
}

func storeConcept(word string, ch chan int) {
  if strings.Contains(word, "/") {
    ch <- 1
    return
  }
  conceptnetUrl := "http://conceptnet5.media.mit.edu/data/5.1/c/en/" + word
  results := fetch(conceptnetUrl)
  marshalled, err := json.Marshal(results)
  errorify(err)
  err = ioutil.WriteFile("./words/" + word + ".json", []byte(marshalled), 0755)
  errorify(err)
  ch <- 1
}

func main() {
  questionString, _ := ioutil.ReadFile("questions.txt")
  splitQs := strings.Fields(string(questionString))
  ch := make(chan int, 1000)
  
  for _, v := range splitQs {
    go storeConcept(v, ch)
    <-ch
  }
}



package main

import (
	"fmt"
	"math"
)


func main() {

	printMe()
	

	fmt.Println("My last name is Rahman")

	fmt.Println(intDivsion(3, 3))
	fmt.Println(floatDivision(56.7, 30.7))

	var myString = []rune("rèsume")

	var indexed = myString[1]

	for indx, value :=range myString{
		fmt.Println(indx, value)
	}

	fmt.Println(indexed)
}

func intDivsion(numerator int, denominator int) int {
	return numerator / denominator
}

func floatDivision(floatNum1 float32, floatNum2 float32) (float32, float32, error) {
	var err error
	var result float32 = floatNum1 / floatNum2
	reminder := math.Mod(float64(floatNum1), float64(floatNum2))
	return result, float32(reminder), err
}

func learnArray(arr []int){
	for i :=range arr{
		fmt.Printf("The calc %v \n", arr[i])
	}
}


func learnMap(first map[string]int32) {
	for key, value := range first{
		fmt.Printf("The key is %v and the value is %v \n", key, value)
	}
	
}
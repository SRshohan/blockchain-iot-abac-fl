import today from "../node_js/mymodule.js";


let name = "John";
const firstName = "John";

let person = {  // Object
    name: "John",
    age: 30
};


let selectionColors = ["black", "white", 255]; // Array

// Function
function greet(name){
    console.log("Hello " + name);
}


// Function with arrow function
let sum = (a, b) => {
    return a + b;
};

// Asynchronous function and await
let fullName = () => {
    setTimeout(() => {
        return greet("John Doe");
    }, 2000);
};


let multiply = async (a, b) => {
    return a * b;
};

multiply(10, 20)
    .then(result => console.log(result));  // 200

Object.entries(person).forEach(([key, value]) => {
    console.log(key+ ":" + value); 
  });



// Can not be contain space or hyphen (-)
console.log(today());
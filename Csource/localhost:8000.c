
int threebai(int number){
    number = number+number;
    number = number+number;
    return number;
}
                    
int twoBai(int number){
    number = threebai(number);
    return number*2;
}
                    
int main(){
    int a = 30;
    int b = 40;
    b = twoBai(b);
    return 0;
}
                
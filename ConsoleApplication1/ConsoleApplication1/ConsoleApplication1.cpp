#include <iostream>
#include <fstream>

using namespace std;

int main()
{
    ifstream FileIn; //Khai báo 1 biến FileIn để đọc dữ liệu

    FileIn.open("C:\\Users\\asus\\Desktop\\filetxt.txt", ios_base::in);

    if (FileIn.fail() == true)
    {
        cout << "File khong ton tai" << endl;
        return 0;
    }

    int x;
    int y;
    FileIn >> x;
    FileIn >> y;
    int sum = x + y;
    cout << "Sum is : " << sum << endl;

    FileIn.close();

    ofstream FileOut;
    FileOut.open("C:\\Users\\asus\\Desktop\\fileout.txt", ios_base::out);
    FileOut << sum;
    FileOut.close();

    cout << "Successfull" << endl;
    system("pause");

    return 0;
}


#include <stdio.h>
#include <string.h> 
#include <stdlib.h>
#include <time.h> 
#include <stdbool.h>
#include <math.h> 
#include <float.h> 
#include <limits.h> 
#include "tflDepthToPoints.h"

int random(int minN, int maxN);
 
int main()
{ 
    initXYZHandler();
    printf("Start \n");
    unsigned short _fake_frame[307200]; // 2byte 
    Vec3 Buffermet[307200];
    unsigned char buffer[614400]; /// 1byte 
    int length = 0;

    FILE *ptr;
    ptr = fopen("depth.bin","rb");  // r for read, b for binary    
    if (!ptr){
        printf("File not found \n");
    }
    fread(buffer,sizeof(buffer),1,ptr); 
    fclose(ptr);
     
	int max_point = 307200;
    FILE *pt;
    pt = fopen("Points-Codex64.ply","w+");  //  Write ply file
		fprintf(pt, "ply\nformat ascii 1.0\nelement vertex %d\nproperty float x\nproperty float y\nproperty float z\nend_header\n", max_point);       
    if (!pt){
        printf("File not found \n");
    } 
         
    for (int i = 0; i < 614400; i=i+2) //byte --> ushort ( 2byte)
    {
        int count_fake=i/2;
        _fake_frame[count_fake]= buffer[i+1];
        _fake_frame[count_fake] = _fake_frame[count_fake]<<8;

        int seed = 0;
        if (i % 31 == 0)
        {
            seed = random(1, 100);
        }
        _fake_frame[count_fake] |= buffer[i] + (unsigned short)seed;         
    } 
    length = sizeof(_fake_frame) / sizeof(_fake_frame[0]) ;    
        
    //Start CreateMesh 
    Vec3 *mesh_xyz  = depthZToXYZ(_fake_frame, length);      
    if(mesh_xyz == NULL)
        printf ("Value Error %f ---AB-- \n",mesh_xyz);  // = NULL == 0 --> Return Error 24 03 2020 
    for (int i = 0 ; i < length; i++)
    { 
        Buffermet[i].x = mesh_xyz[i].x;
        Buffermet[i].y = mesh_xyz[i].y;
        Buffermet[i].z = mesh_xyz[i].z; 
           
        fprintf (pt, "%f %f %f\n", Buffermet[i].x, Buffermet[i].y, Buffermet[i].z);
    } 
         
    fclose(pt);

    releaseXYZHandler(); //release memory leak
    
    //End CreateMesh
    printf("FINISHED \n");
}


int random(int minN, int maxN)
{
    return minN + rand() % (maxN + 1 - minN);
}

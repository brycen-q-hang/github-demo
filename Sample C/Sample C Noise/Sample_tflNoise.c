#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "tflNoise.h"
#include <stdbool.h>
#include <time.h>

int main()
{
  initNoiseHandler();

  Vec3 *dataInput = (Vec3*)calloc(max_point, sizeof(Vec3));

  FILE *File_input; 
  File_input = fopen("data.ply", "r");
  char str[MAXCHAR];
    
    if(File_input == NULL)
  	{
		printf("ERR: Read file");
	   	exit(EXIT_FAILURE);
      return 0;
	  } 
    int Count_array = 0;
    
    while (fgets(str,MAXCHAR, File_input) != NULL)
    {
   
        int XYZ = 0;
        char *p = strtok(str, " ");

        while( p != NULL ) 
  	    {
  	    	if(XYZ == 0)
  	    	{
  	    		dataInput[Count_array].X = strtod(p,NULL);
			    }
			
          if(XYZ == 1)
          {
            dataInput[Count_array].Y = strtod(p,NULL);
          }
			
          if(XYZ == 2)
          {
            dataInput[Count_array].Z = strtod(p,NULL);
          }
			
		      XYZ ++;
			    p = strtok(NULL, " ");
        }
       
        Count_array ++;
        if (Count_array == max_point)
        {
          break;
        }
    }
  fclose(File_input);
  printf(" __ FINISH __ ");

  float radius = 19;

  FILE *File_output;
  File_output = fopen("Noise-Codex64.ply", "w");
  bool *dataOutput = markNoise(dataInput,radius,640,480); 
  fprintf(File_output,"ply\nformat ascii 1.0\nelement vertex 307200\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n");
  for (int i = 0; i < max_point; i++)
  {
    if (dataOutput[i] == false) //Non Noise
    {
      //numdata ++;
      fprintf(File_output,"%0.2f %0.2f %0.1f 255 255 255 \n", dataInput[i].X, dataInput[i].Y,dataInput[i].Z);    
    }
    else //Noise
    {        
      fprintf(File_output,"%0.2f %0.2f %0.1f 255 0 0 \n", dataInput[i].X, dataInput[i].Y,dataInput[i].Z);
    }
  }
  fclose(File_output);

  releaseNoiseHandler(); //release memory leak
return 0;  
}
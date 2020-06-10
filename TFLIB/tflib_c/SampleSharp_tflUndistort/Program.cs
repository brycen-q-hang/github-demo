using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.IO;
using System.Drawing;

namespace SampleSharp_tflUndistort
{
	class Program
	{
        [DllImport("tflib_c.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr Undistort(ushort[] depthBuf,ushort[] depthBufUnDistorted);

        static void Main(string[] args)
		{ 
            Console.WriteLine("-- START --"); 
             
            ushort[] _fake_frame = null;

            if (_fake_frame == null)
            {

                _fake_frame = new ushort[307200];

              
                string path_fake_depth = "depth.bin";     //  Read depth.bin file

                FileInfo fi = new FileInfo(path_fake_depth);


                FileStream _fileStream = new FileStream(path_fake_depth, FileMode.Open);
                BinaryReader __binaryReader = new BinaryReader(_fileStream);

                // file ushort array
                int __currentPosInStream = 0;
                int ___lengthOfStream = (int)__binaryReader.BaseStream.Length;
                int i = 0;
                while (__currentPosInStream < ___lengthOfStream)
                {
                    ushort ushortDepth = __binaryReader.ReadUInt16();
                    _fake_frame[i] = ushortDepth;

                    __currentPosInStream += sizeof(ushort);
                    i++;
                }
            }
             
            ushort[] depthBufUnDistorted = new ushort[307200];

            Stopwatch cout = new Stopwatch();
            cout.Start();
            
            //  UndistortLens funtion 
            IntPtr result = Undistort(_fake_frame, depthBufUnDistorted);

            cout.Stop();
            
            Console.WriteLine("Result: " + result);

            Console.WriteLine("Time after Undistort Depth File-->{0}", cout.ElapsedMilliseconds);

            FileStream fs = new FileStream("Data_Undistort.csv", FileMode.Create);
            StreamWriter sw = new StreamWriter(fs);

            using (sw)
            {
                for (int i = 0; i < 307200; i++)
                {
                    sw.WriteLine("NO[{0}]  =  {1} ", i, depthBufUnDistorted[i]);
                }
                sw.Close();
            }

            Console.WriteLine("-- FINISH --");
            Console.ReadKey();
        }
	}
}

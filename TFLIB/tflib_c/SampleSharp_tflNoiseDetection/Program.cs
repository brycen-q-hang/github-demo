using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.IO;
using System.Drawing;

namespace SampleSharp_tflNoiseDetection
{
    class Program
    {
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
        public struct TFL_PointXYZ
        {
            public float x;
            public float y;
            public float z;
        };

        [DllImport("tflib_c.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr MarkPCDNoise(TFL_PointXYZ[] pcdFullBuf, ushort sensitiveFactor, IntPtr noiseFlag, out uint num_noise);

        static void Main(string[] args)
        {
            Console.WriteLine("-- START --");
            Console.WriteLine("-- DETECTION NOISE --");

            string[] lines = File.ReadAllLines("data.ply");
            int max_point = 307200;

            TFL_PointXYZ[] pcdFullBuf = new TFL_PointXYZ[307200];
            ushort sensitiveFactor = 10;
            int n = 0;            

            for (int i = 0; i < 307200; i++)
            {
                if (lines[i].Length == 0)
                {
                    //Console.WriteLine("Error here !!!");
                }
                else
                {
                    string[] words = lines[i].Split(' ');
                    float.TryParse(words[0], out pcdFullBuf[i].x);
                    float.TryParse(words[1], out pcdFullBuf[i].y);
                    float.TryParse(words[2], out pcdFullBuf[i].z);
                    n++;
                }
            }

            var size__ = Marshal.SizeOf(typeof(TFL_PointXYZ));
            IntPtr noiseFlag = Marshal.AllocHGlobal(12 * 307200);
            byte[] boo__ = new byte[307200];
            uint num_noise = 0;

            IntPtr result = MarkPCDNoise(pcdFullBuf, sensitiveFactor, noiseFlag, out num_noise);
            Console.WriteLine("Return is: {0}", result);

            for (int j = 0; j < 307200; j++)
            {
                IntPtr ins = new IntPtr(noiseFlag.ToInt64() + j * size__);
                boo__[j] = Marshal.PtrToStructure<byte>(ins);                
            }

            Console.WriteLine("Num noise is : {0}", num_noise);
            FileStream dt_noise = new FileStream("PCL_Noise.ply", FileMode.Create);
            StreamWriter clr_noise = new StreamWriter(dt_noise);

            clr_noise.WriteLine("ply\nformat ascii 1.0\nelement vertex {0}\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header", max_point);

            for (int k = 0; k < max_point; k++)
            {
                if (boo__[k] == 0)
                {
                    clr_noise.WriteLine("{0} {1} {2} 255 255 255", pcdFullBuf[k].x, pcdFullBuf[k].y, pcdFullBuf[k].z);
                }
                else
                {
                    clr_noise.WriteLine("{0} {1} {2} 255 0 0", pcdFullBuf[k].x, pcdFullBuf[k].y, pcdFullBuf[k].z);
                }
            }

            clr_noise.Close();

            Console.WriteLine("-- FINISH --");
            Console.ReadKey();
        }
    }
}

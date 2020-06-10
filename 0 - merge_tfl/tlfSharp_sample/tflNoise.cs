using System;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.IO;

namespace tlfSharp_sample
{
    class tflNoise
    {
        public struct Vector_3
        {
            public float X;
            public float Y;
            public float Z;
        }

        [DllImport("tfl.dll", EntryPoint = "markNoise", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr markNoise(Vector_3[] data, float radius, int sensor_W, int sensor_H);

        [DllImport("tfl.dll", EntryPoint = "initNoiseHandler", CallingConvention = CallingConvention.Cdecl)]
        public static extern void initNoiseHandler();

        static void Main(string[] args)
        {
            initNoiseHandler();
            string[] lines = File.ReadAllLines("data.ply");
            int max_point = 307200;
            Vector_3[] Vector2 = new Vector_3[307200];
            float radius = 10;
            int n = 0;
            int numnoise = 0;

            for (int i = 0; i < 307200; i++)
            {
                if (lines[i].Length == 0)
                {
                    //Console.WriteLine("Error here !!!");
                }
                else
                {
                    string[] words = lines[i].Split(' ');
                    float.TryParse(words[0], out Vector2[i].X);
                    float.TryParse(words[1], out Vector2[i].Y);
                    float.TryParse(words[2], out Vector2[i].Z);
                    n++;
                }
            }

            var size = Marshal.SizeOf(typeof(byte));
            byte[] boo__ = new byte[307200];


            IntPtr ptr = markNoise(Vector2, radius, 640, 480);

            for (int j = 0; j < 307200; j++)
            {
                IntPtr ins = new IntPtr(ptr.ToInt64() + j * size);
                boo__[j] = Marshal.PtrToStructure<byte>(ins);

            }

            FileStream dt_noise = new FileStream("Noise_x64Ply.ply", FileMode.Create);
            StreamWriter clr_noise = new StreamWriter(dt_noise);

            clr_noise.WriteLine("ply\nformat ascii 1.0\nelement vertex {0}\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header", max_point);

            for (int k = 0; k < max_point; k++)
            {
                if (boo__[k] == 0)
                {
                    clr_noise.WriteLine("{0} {1} {2} 255 255 255", Math.Round(Vector2[k].X, 2), Math.Round(Vector2[k].Y, 2), Math.Round(Vector2[k].Z, 1));
                }
                else
                {
                    clr_noise.WriteLine("{0} {1} {2} 255 0 0", Math.Round(Vector2[k].X, 2), Math.Round(Vector2[k].Y, 2), Math.Round(Vector2[k].Z, 1));
                }
            }

            clr_noise.Close();

            Console.WriteLine(" -- FINISH -- ");
            Console.ReadKey();
        }
    }
}

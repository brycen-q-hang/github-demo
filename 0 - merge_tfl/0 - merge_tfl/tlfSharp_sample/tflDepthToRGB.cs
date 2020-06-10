using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.IO;
using System.Drawing;

namespace tlfSharp_sample
{
    class tflDepthToRGB
    {
        public struct Vector_3
        {
            public float x;
            public float y;
            public float z;
        }

        [DllImport("tfl.dll", EntryPoint = "initRGBHandler", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr initRGBHandler();

        [DllImport("tfl.dll", EntryPoint = "depthToRainbow", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr depthToRainbow(ushort[] array, int length);

        [DllImport("tfl.dll", EntryPoint = "depthToGrayscale", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr depthToGrayscale(ushort[] array, int length);

        [DllImport("tfl.dll", EntryPoint = "releaseRGBHandler", CallingConvention = CallingConvention.Cdecl)]
        public static extern void releaseRGBHandler();

        static void Main(string[] args)
        {
            initRGBHandler();

            Console.WriteLine("START CREATEMESH");
            Random random = new Random();

            ushort[] __nextTOF_Frame_DEPTH_data = new ushort[307200];
            ushort[] _fake_frame = null;

            if (_fake_frame == null)
            {

                _fake_frame = new ushort[307200];


                Console.WriteLine("Hello World!");

                string path_fake_depth = "depth.bin";

                FileInfo fi = new FileInfo(path_fake_depth);


                FileStream _fileStream = new FileStream(path_fake_depth, FileMode.Open);
                BinaryReader __binaryReader = new BinaryReader(_fileStream);

                // file ushort array
                int __currentPosInStream = 0;
                int ___lengthOfStream = (int)__binaryReader.BaseStream.Length; //= 307200*2
                int i = 0;
                Console.WriteLine(___lengthOfStream);
                while (__currentPosInStream < ___lengthOfStream)
                {
                    ushort ushortDepth = __binaryReader.ReadUInt16();
                    _fake_frame[i] = ushortDepth;
                    __currentPosInStream += sizeof(ushort);
                    i++;
                }
            }

            int b = 0;
            for (int i = 0; i < _fake_frame.Length; i++)
            {
                // cnt++;

                int seed = 0;
                if (i % 31 == 0)
                {
                    seed = random.Next(0, 100);
                }
                // d_vu - update depth array - 20200216
                __nextTOF_Frame_DEPTH_data[i] = (ushort)(_fake_frame[i] + seed);
            }

            var size = Marshal.SizeOf(typeof(Vector_3));
            Vector_3[] mesh_xyz = new Vector_3[_fake_frame.Length];
            Vector_3[] RGB = new Vector_3[_fake_frame.Length];

            FileStream fs = new FileStream("RGB_x64Ply.ply", FileMode.Create);
            StreamWriter sw = new StreamWriter(fs);

            IntPtr pth = depthToRainbow(_fake_frame, _fake_frame.Length);

            using (sw)
            {
                sw.WriteLine("ply");
                sw.WriteLine("format ascii 1.0");
                sw.WriteLine("element vertex 307200");
                sw.WriteLine("property uchar red");
                sw.WriteLine("property uchar green");
                sw.WriteLine("property uchar blue");

                sw.WriteLine("end_header");
                for (int ba = 0; ba < _fake_frame.Length; ba++)
                {
                    IntPtr ins = new IntPtr(pth.ToInt64() + ba * size);
                    RGB[ba] = Marshal.PtrToStructure<Vector_3>(ins);

                    sw.WriteLine("{0} {1} {2}", RGB[ba].x, RGB[ba].y, RGB[ba].z);
                }
                sw.Close();
            }
            releaseRGBHandler(); //release memory leak
            Console.WriteLine("FNISHED");
            Console.ReadKey();

        }
    }
}

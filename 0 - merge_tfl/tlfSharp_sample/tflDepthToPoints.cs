using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Diagnostics;
using System.IO;
//using System.Numerics;

using System.Runtime.InteropServices;

namespace tlfSharp_sample
{
    class tflDepthToPoints
    {
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
        public struct Vector_3
        {
            public float x;
            public float y;
            public float z;
        };

        [DllImport("tfl.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern void initXYZHandler();

        [DllImport("tfl.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr depthZToXYZ(ushort[] _depthRaw, int length_depthRaw);

        [DllImport("tfl.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern void releaseXYZHandler();

        static void Main(string[] args)
        {
            initXYZHandler();

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

            FileStream fs = new FileStream("Points_x64Ply.ply", FileMode.Create);
            StreamWriter sw = new StreamWriter(fs);


            Stopwatch cout = new Stopwatch();
            cout.Start();

            IntPtr pth = depthZToXYZ(_fake_frame, _fake_frame.Length);
            Console.WriteLine("Value of Error  " + pth);

            using (sw)
            {
                sw.WriteLine("ply");
                sw.WriteLine("format ascii 1.0");
                sw.WriteLine("element vertex 307200");
                sw.WriteLine("property float x");
                sw.WriteLine("property float y");
                sw.WriteLine("property float z");

                sw.WriteLine("end_header");
                for (int ba = 0; ba < _fake_frame.Length; ba++)
                {
                    IntPtr ins = new IntPtr(pth.ToInt64() + ba * size);
                    mesh_xyz[ba] = Marshal.PtrToStructure<Vector_3>(ins);
                    sw.WriteLine("{0} {1} {2}", mesh_xyz[ba].x, mesh_xyz[ba].y, mesh_xyz[ba].z);
                }
                sw.Close();
            }
            cout.Stop();
            Console.WriteLine("Time after CreateMesh and Create Ply file -->{0}", cout.ElapsedMilliseconds);
            b++;
            releaseXYZHandler();  // Remove Memory Leak 
                                  ///code Test

            Console.WriteLine("FNISHED");
            Console.ReadKey();
        }
    }
}

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.IO;
using System.Drawing;

namespace SampleSharp_tflDepthPCD
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
        public static extern IntPtr DepthToPCD(ushort[] depthBuf, IntPtr pcdBuf);

        static void Main(string[] args)
        {
            Console.WriteLine("-- START --");
            Console.WriteLine("-- DEPTHPCD --");
            
            Random random = new Random();
            ushort[] __nextTOF_Frame_DEPTH_data = new ushort[307200];
            ushort[] _fake_frame = null;

            if (_fake_frame == null)
            {

                _fake_frame = new ushort[307200];                

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
            
            for (int i = 0; i < _fake_frame.Length; i++)
            {
                // cnt++;

                int seed = 0;
                if (i % 31 == 0)
                {
                    seed = random.Next(0, 100);
                }
                
                __nextTOF_Frame_DEPTH_data[i] = (ushort)(_fake_frame[i] + seed);
            }

            var size = Marshal.SizeOf(typeof(TFL_PointXYZ));
            TFL_PointXYZ[] mesh_xyz = new TFL_PointXYZ[_fake_frame.Length];
            FileStream fs = new FileStream("PCL_PointXYZ.ply", FileMode.Create);
            StreamWriter sw = new StreamWriter(fs);

            Stopwatch cout = new Stopwatch();
            cout.Start();

            var size__ = Marshal.SizeOf(typeof(TFL_PointXYZ));
            IntPtr pcdBuf = Marshal.AllocHGlobal(12 * 307200);

            TFL_PointXYZ[] points__ = new TFL_PointXYZ[307200];

            IntPtr result = DepthToPCD(_fake_frame, pcdBuf);
            Console.WriteLine("Return : {0}", result);
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
                    IntPtr ins = new IntPtr(pcdBuf.ToInt64() + ba * size);
                    mesh_xyz[ba] = Marshal.PtrToStructure<TFL_PointXYZ>(ins);
                    sw.WriteLine("{0} {1} {2}", mesh_xyz[ba].x, mesh_xyz[ba].y, mesh_xyz[ba].z);
                }
                sw.Close();
            }
            cout.Stop();
            Console.WriteLine("Time after CreateMesh and Create Ply file -->{0}", cout.ElapsedMilliseconds);

            Console.WriteLine("-- FINISH --");
            Console.ReadKey();
        }
    }
}

#define PCL_RGB
//#define PCL_Grayscale
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.IO;
using System.Drawing;

namespace SampleSharp_tflColorMapping
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
        public static extern IntPtr DepthToRainbow(ushort[] depthBuf, int displayMin, int displayMax, IntPtr depthColor);

        [DllImport("tflib_c.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr DepthToGray(ushort[] depthBuf, ushort displayMin, ushort displayMax, IntPtr depthColor);

        static void Main(string[] args)
        {
            Console.WriteLine("-- START --");
            Console.WriteLine("-- COLOR MAPPING --");
            
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

            TFL_PointXYZ[] mesh_xyz = new TFL_PointXYZ[_fake_frame.Length];
            TFL_PointXYZ[] RGB = new TFL_PointXYZ[_fake_frame.Length];

            FileStream fs = new FileStream("RGB_x64Ply.ply", FileMode.Create);
            StreamWriter sw = new StreamWriter(fs);

            var size__ = Marshal.SizeOf(typeof(TFL_PointXYZ));
            IntPtr depthColor = Marshal.AllocHGlobal(15 * 307200);

            TFL_PointXYZ[] points__ = new TFL_PointXYZ[307200];
#if PCL_RGB
            IntPtr result = DepthToRainbow(_fake_frame, 600, 6000, depthColor);
#endif

#if PCL_Grayscale
            IntPtr result = DepthToGray(_fake_frame, 65525, 0, depthColor);
#endif
            Console.WriteLine("Return is: {0}", result);

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
                    IntPtr ins = new IntPtr(depthColor.ToInt64() + ba * size__);
                    RGB[ba] = Marshal.PtrToStructure<TFL_PointXYZ>(ins);

                    sw.WriteLine("{0} {1} {2}", RGB[ba].x, RGB[ba].y, RGB[ba].z);
                }
                sw.Close();
            }

            Console.WriteLine("-- FINISH --");
            Console.ReadKey();

        }
    }
}

using System;
using System.Runtime.InteropServices;

namespace tflSharp
{
    public class tflNoise
    {
        [DllImport("tfl", EntryPoint = "initNoiseHandler", CallingConvention = CallingConvention.Cdecl)]
        static extern void nt_initNoiseHandler();

        [DllImport("tfl", EntryPoint = "markNoise", CallingConvention = CallingConvention.Cdecl)]
        static extern IntPtr nt_markNoise(Vec3[] data, float r, int sensor_w, int sensor_h, out uint num_noise);

        [DllImport("tfl", EntryPoint = "releaseNoiseHandler", CallingConvention = CallingConvention.Cdecl)]
        static extern void nt_releaseNoiseHandler();

        private static tflNoise _ist = null;

        public static tflNoise GetInstance()
        {
            if (_ist == null)
            {
                _ist = new tflNoise();
            }

            return _ist;
        }

        private tflNoise()
        {
            _init();
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="data"></param>
        /// <param name="r"></param>
        /// <param name="sensor_w"></param>
        /// <param name="sensor_h"></param>
        /// <param name="num_noise"></param>
        /// <returns></returns>
        public bool[] markNoise(Vec3[] data, float r, int sensor_w, int sensor_h, out uint num_noise)
        {
            bool[] flgs = new bool[data.Length];
            
            IntPtr ptr = nt_markNoise(data, r, sensor_w, sensor_h, out num_noise);
            long _long_ptr = ptr.ToInt64();
            for (int jj = 0; jj < sensor_w * sensor_h; jj++)
            {
                IntPtr ins = new IntPtr(_long_ptr + jj * 1);
                flgs[jj] = Marshal.PtrToStructure<bool>(ins);
            }

            return flgs;
        }

        private void _init()
        {
            nt_initNoiseHandler();
        }

        public void Release()
        {
            nt_releaseNoiseHandler();
        }
    }
}

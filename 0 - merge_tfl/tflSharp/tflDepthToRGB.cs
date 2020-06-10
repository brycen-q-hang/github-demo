using System;
using System.Runtime.InteropServices;

namespace tflSharp
{
    public class tflDepthToRGB
    {
        [DllImport("tfl", EntryPoint = "initRGBHandler", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr nt_initRGBHandler();

        [DllImport("tfl", EntryPoint = "depthToRainbow", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr nt_depthToRainbow(ushort[] array, int length);

        [DllImport("tfl", EntryPoint = "depthToGrayscale", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr nt_depthToGrayscale(ushort[] array, int length);

        [DllImport("tfl", EntryPoint = "releaseRGBHandler", CallingConvention = CallingConvention.Cdecl)]
        public static extern void nt_releaseDepthRGBHandler();

        private static tflDepthToRGB _ist = null;

        public static tflDepthToRGB GetInstance()
        {
            if (_ist == null)
            {
                _ist = new tflDepthToRGB();
            }

            return _ist;
        }

        private tflDepthToRGB()
        {
            _init();
        }

        private void _init()
        {
            nt_initRGBHandler();
        }

        int intptr_data_size = Marshal.SizeOf(typeof(Vec4));
        public Vec4[] depthToGrayscale(ushort[] array)
        {
            Vec4[] arr_vec4 = new Vec4[array.Length];

            // mem handler
            IntPtr intPtr = nt_depthToGrayscale(array, array.Length);
            long _long_intptr = intPtr.ToInt64();

            for (int i = 0; i < array.Length; i++)
            {
                IntPtr __ptr = new IntPtr(_long_intptr + i * intptr_data_size);
                Vec4 v = Marshal.PtrToStructure<Vec4>(__ptr);
                v.a = 1.0f;

                arr_vec4[i] = v;
            }

            return arr_vec4;
        }

        public Vec4[] depthToRainbow(ushort[] array)
        {
            Vec4[] arr_vec4 = new Vec4[array.Length];

            // mem handler
            IntPtr intPtr = nt_depthToRainbow(array, array.Length);
            long _long_intptr = intPtr.ToInt64();

            for (int i = 0; i < array.Length; i++)
            {
                IntPtr __ptr = new IntPtr(_long_intptr + i * intptr_data_size);
                Vec4 v = Marshal.PtrToStructure<Vec4>(__ptr);
                v.a = 1.0f;

                arr_vec4[i] = v;
            }

            return arr_vec4;
        }

        public void Release()
        {
            nt_releaseDepthRGBHandler();
        }
    }
}

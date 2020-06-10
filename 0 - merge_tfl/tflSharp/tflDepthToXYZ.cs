using System;
using System.Runtime.InteropServices;

namespace tflSharp
{
    public class tflDepthToXYZ
    {
        [DllImport("tfl", EntryPoint = "initXYZHandler", CallingConvention = CallingConvention.Cdecl)]
        public static extern void nt_initXYZHandler();

        [DllImport("tfl", EntryPoint = "depthToPointsXYZ", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr nt_depthToPointsXYZ(ushort[] depthArray, int size);

        [DllImport("tfl", EntryPoint = "releaseXYZHandler", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr nt_releaseXYZHandler();

        private static tflDepthToXYZ _ist = null;

        public static tflDepthToXYZ GetInstance()
        {
            if (_ist == null)
            {
                _ist = new tflDepthToXYZ();
            }

            return _ist;
        }

        private tflDepthToXYZ()
        {
            _init();
        }

        private void _init()
        {            
            nt_initXYZHandler();
        }

        int vec3_size = Marshal.SizeOf(typeof(Vec3));
        public Vec3[] depthToPointsXYZ(ushort[] depthArray)
        {
            Vec3[] arr_vec3 = new Vec3[depthArray.Length];

            // execute function in nativeLib
            IntPtr intPtr = nt_depthToPointsXYZ(depthArray, depthArray.Length);

            // apply to mesh
            long long_IntPtr = intPtr.ToInt64();
            for (int i = 0; i < depthArray.Length; i++)
            {
                IntPtr ins = new IntPtr(long_IntPtr + i * vec3_size);
                Vec3 v = Marshal.PtrToStructure<Vec3>(ins);
            }

            return arr_vec3;
        }

        public void Release()
        {
            nt_releaseXYZHandler();
        }
    }
}

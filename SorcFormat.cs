using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using CharactorLib.Common;
using CharactorLib.Format;
using CharactorLib.Data;
using System.Drawing;

namespace SorcFormat
{
	/// <summary>
	/// 2bpp NES
	/// </summary>
	public class TestFormat : FormatBase
	{

		/// <summary>
		/// Constructor.
		/// </summary>
		public TestFormat()
		{
			base.FormatText = "[8][8]";
			base.Name = "Sorcerian Alphaless";
			base.Extension = "test";
			base.Author = "TWE";
			base.Url = "";
			// Flags
			base.Readonly = false;
			base.IsCompressed = false;
			base.EnableAdf = true;
			base.IsSupportMirror = false;
			base.IsSupportRotate = false;
			// Settings
			base.ColorBit = 4;
			base.ColorNum = 8;
			base.CharWidth = 16;
			base.CharHeight = 8;
			// Settings for Image Convert
			base.Width = 128;
			base.Height = 128;

		}

		/// <summary>
		/// Charactor Convert.
		/// </summary>
		/// <param name="data">Data</param>
		/// <param name="addr">Data address</param>
		/// <param name="bytemap">Bytemap</param>
		/// <param name="px">Bytemap position X</param>
		/// <param name="py">Bytemap position Y</param>
		public override void ConvertMemToChr(Byte[] data, int addr, Bytemap bytemap, int px, int py)
		{
			byte[] bit_scan = new byte[8];

			for (int y = 0; y < CharHeight; y++)
			{
				for (int pl = 0; pl < ColorBit; pl++)
				{
					int tmp = addr + pl * 0x10 + y * 2;
					bit_scan[pl] = data[tmp];
					bit_scan[pl + 4] = data[tmp + 1];
				}

				for (int x = 0; x < 8; x++)
				{
					int b1 = ((bit_scan[0] & 0x01)  | ((bit_scan[1] & 0x01) << 1)  | ((bit_scan[2] & 0x01) << 2) | ((bit_scan[3] & 0x01) << 3));
					int b2 = ((bit_scan[4] & 0x01)  | ((bit_scan[5] & 0x01) << 1)  | ((bit_scan[6] & 0x01) << 2) | ((bit_scan[7] & 0x01) << 3));

					for (int i=0; i<8; i++)
                    {
						bit_scan[i] >>= 1;
                    }

					Point p = base.GetAdvancePixelPoint(px + (7-x), py + y);
					int bytemapAddr = bytemap.GetPointAddress(p.X, p.Y);
					bytemap.Data[bytemapAddr] = (byte)b1;

					p = base.GetAdvancePixelPoint(px + (7-x) + 8, py + y);
					bytemapAddr = bytemap.GetPointAddress(p.X, p.Y);
					bytemap.Data[bytemapAddr] = (byte)b2;
				}
			}
		}

		/// <summary>
		/// Charactor Convert.
		/// </summary>
		/// <param name="data">Data</param>
		/// <param name="addr">Data address</param>
		/// <param name="bytemap">Bytemap</param>
		/// <param name="px">Bytemap position X</param>
		/// <param name="py">Bytemap position Y</param>
		public override void ConvertChrToMem(Byte[] data, int addr, Bytemap bytemap, int px, int py)
		{

			for(int y=0; y<CharHeight; y++)
            {
				int bAddr = addr + y*2;

				byte[] b1 = new byte[4];
				byte[] b2 = new byte[4];

				for(int x=0; x<8; x++)
                {
					Point p1 = base.GetAdvancePixelPoint(px + x, py + y);
					int bytemapAddr1 = bytemap.GetPointAddress(p1.X, p1.Y);
					int value1 = bytemap.Data[bytemapAddr1];
					Point p2 = base.GetAdvancePixelPoint(px + x + 8, py + y);
					int bytemapAddr2 = bytemap.GetPointAddress(p2.X, p2.Y);
					int value2 = bytemap.Data[bytemapAddr2];


					for (int pl=0; pl<ColorBit; pl++)
                    {
						b1[pl] |= (byte)(((value1 >> pl) & 0x01) << (7 - x));
						b2[pl] |= (byte)(((value2 >> pl) & 0x01) << (7 - x));
					}
				}

				for(int pl=0; pl<ColorBit; pl++)
                {
					data[bAddr + pl * 0x10] = b1[pl];
					data[bAddr + pl * 0x10 + 1] = b2[pl];
				}
			}

		}


	}
}

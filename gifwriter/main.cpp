#include "gifwriter.h"
#include <QImage>
#include <vector>
#include <QFile>

int main()
{
  std::vector<QImage> frames;
  for (auto color : { Qt::blue, Qt::yellow, Qt::darkCyan }) {
    frames.push_back(QImage(64, 64, QImage::Format_ARGB32));
    frames.back().fill(color);
  }

  QFile file("sample.gif");
  if (file.open(QIODevice::WriteOnly)) {
    int delay = 200; // ms
    bool dither = false;
    const auto data = GifWriter::encode(frames, delay, dither);
    file.write(data);
    exit(0);
  } else {
    exit(1);
  }
}


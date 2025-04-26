import 'package:flutter/material.dart';

class InfiniteScrollBackground extends StatefulWidget {
  const InfiniteScrollBackground({super.key});

  @override
  State<InfiniteScrollBackground> createState() =>
      _InfiniteScrollBackgroundState();
}

class _InfiniteScrollBackgroundState extends State<InfiniteScrollBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  double _imageWidth = 0;
  final _scrollSpeed = 10.0;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(hours: 1),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            final elapsedTime =
                _controller.lastElapsedDuration?.inMilliseconds ?? 0;
            final offset =
                (elapsedTime / 1000.0 * _scrollSpeed) % (_imageWidth);

            return Stack(
              children: [
                Positioned(
                  left: -offset,
                  child: Row(
                    children: [
                      _buildImage(),
                      _buildImage(),
                    ],
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Widget _buildImage() {
    return Image.asset(
      'assets/images/Cloud background.png',
      fit: BoxFit.contain,
      width: 1280,
      height: 354,
      // Capture the width only once to help calculate looping
      // (assumes full screen width for background tile)
      key: UniqueKey(), // prevents Flutter from recycling
      frameBuilder: (context, child, frame, wasSynchronouslyLoaded) {
        if (_imageWidth == 0) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            final renderBox = context.findRenderObject() as RenderBox?;
            if (renderBox != null) {
              setState(() {
                _imageWidth = renderBox.size.width;
              });
            }
          });
        }
        return child;
      },
    );
  }
}

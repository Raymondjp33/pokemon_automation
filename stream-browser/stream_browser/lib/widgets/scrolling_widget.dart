import 'package:flutter/material.dart';

class ScrollingWidget extends StatefulWidget {
  const ScrollingWidget({
    required this.child,
    this.scrollSpeed = 10.0,
    super.key,
  });

  final Widget child;
  final double scrollSpeed;

  @override
  State<ScrollingWidget> createState() => _ScrollingWidgetState();
}

class _ScrollingWidgetState extends State<ScrollingWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  final GlobalKey _childKey = GlobalKey();
  double _childWidth = 0;

  @override
  void initState() {
    super.initState();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final context = _childKey.currentContext;
      if (context != null && mounted) {
        final box = context.findRenderObject() as RenderBox;
        setState(() {
          _childWidth = box.size.width;
        });
      }
    });

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
            final offset = (elapsedTime / 1000.0 * widget.scrollSpeed) %
                (_childWidth == 0 ? 1 : _childWidth);
            return Stack(
              children: [
                Positioned(
                  left: -offset,
                  child: Row(
                    children: [
                      KeyedSubtree(
                        key: _childKey,
                        child: MeasureSize(
                          onChange: (size) {
                            setState(() => _childWidth = size.width);
                          },
                          child: widget.child,
                        ),
                      ),
                      widget.child,
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
}

typedef OnWidgetSizeChange = void Function(Size size);

class MeasureSize extends StatefulWidget {
  final Widget child;
  final OnWidgetSizeChange onChange;

  const MeasureSize({
    super.key,
    required this.child,
    required this.onChange,
  });

  @override
  State<MeasureSize> createState() => _MeasureSizeState();
}

class _MeasureSizeState extends State<MeasureSize> {
  @override
  Widget build(BuildContext context) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final renderBox = context.findRenderObject() as RenderBox;
      if (renderBox.hasSize) {
        widget.onChange(renderBox.size);
      }
    });

    return widget.child;
  }
}

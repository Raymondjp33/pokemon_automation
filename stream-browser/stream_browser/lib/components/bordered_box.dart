import 'package:flutter/material.dart';

BorderSide containerBorder({width = 5}) => width == 0
    ? BorderSide.none
    : BorderSide(
        color: Color(0xFF4C6CBF),
        width: width,
      );

class BorderedBox extends StatelessWidget {
  const BorderedBox({
    this.width,
    this.height,
    this.left,
    this.right,
    this.top,
    this.bottom,
    this.child,
    this.padding,
    this.filled = false,
    super.key,
  });

  final double? width;
  final double? height;
  final double? left;
  final double? right;
  final double? top;
  final double? bottom;
  final Widget? child;
  final EdgeInsets? padding;
  final bool filled;
  final double defaultBorderSize = 5;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      padding: padding,
      decoration: BoxDecoration(
        color: filled ? Colors.black : null,
        border: Border(
          left: containerBorder(width: left ?? defaultBorderSize),
          right: containerBorder(width: right ?? defaultBorderSize),
          top: containerBorder(width: top ?? defaultBorderSize),
          bottom: containerBorder(width: bottom ?? defaultBorderSize),
        ),
      ),
      child: child,
    );
  }
}

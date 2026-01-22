import 'package:flutter/material.dart';

import '../constants/app_assets.dart';
import '../widgets/scrolling_widget.dart';

class MainBackground extends StatelessWidget {
  const MainBackground({required this.children, super.key});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 1280,
      height: 720,
      child: Stack(
        children: [
          ScrollingWidget(
            child: Image.asset(
              AppAssets.fullBackground, fit: BoxFit.contain,
              width: 1280,
              height: 720,
              // Capture the width only once to help calculate looping
              // (assumes full screen width for background tile)
              key: UniqueKey(), // prevents Flutter from recycling
            ),
          ),
          ...children,
        ],
      ),
    );
  }
}

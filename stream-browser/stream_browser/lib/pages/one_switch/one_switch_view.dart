import 'package:flutter/material.dart';

import '../../constants/app_assets.dart';
import '../../widgets/scrolling_widget.dart';
import '../two_switch/components/main_content/right_switch_content.dart';

BorderSide containerBoarder({width = 5}) => BorderSide(
      color: Color(0xFF4C6CBF),
      width: width,
    );

class OneSwitchView extends StatelessWidget {
  const OneSwitchView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: 1280,
        height: 720,
        decoration: BoxDecoration(),
        child: Center(
          child: Stack(
            children: [
              ScrollingWidget(
                child: Image.asset(
                  AppAssets.oneSwitchBackground, fit: BoxFit.contain,
                  width: 1280,
                  height: 720,
                  // Capture the width only once to help calculate looping
                  // (assumes full screen width for background tile)
                  key: UniqueKey(), // prevents Flutter from recycling
                ),
              ),
              Positioned(
                child: Container(
                  width: 832,
                  height: 476,
                  decoration: BoxDecoration(
                    color: Colors.black,
                    border: Border.fromBorderSide(
                      containerBoarder(),
                    ),
                  ),
                ),
              ),
              Positioned(
                right: 0,
                child: Container(
                  width: 448,
                  height: 476,
                  padding: EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.6),
                    border: Border(
                      right: containerBoarder(),
                      top: containerBoarder(),
                      bottom: containerBoarder(),
                    ),
                  ),
                  child: Align(
                    alignment: Alignment.center,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        RightSwitchContent(),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

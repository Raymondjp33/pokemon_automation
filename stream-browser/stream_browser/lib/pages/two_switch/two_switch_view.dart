import 'package:flutter/material.dart';

import '../../widgets/scrolling_widget.dart';
import 'components/main_content/left_switch_content.dart';
import 'components/middle_content.dart';
import 'components/main_content/right_switch_content.dart';

class TwoSwitchView extends StatelessWidget {
  const TwoSwitchView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Stack(
          children: [
            Container(
              width: 1280,
              height: 354,
              child: ScrollingWidget(
                child: BackgroundImage(),
              ),
            ),
            Container(
              width: 1280,
              height: 354,
              child: Row(
                children: [
                  Container(
                    width: 328,
                    height: 354,
                    padding: EdgeInsets.symmetric(vertical: 10, horizontal: 20),
                    decoration: const BoxDecoration(
                      border: Border(
                        right: BorderSide(width: 5, color: Color(0xFF4C6CBF)),
                      ),
                    ),
                    child: LeftSwitchContent(),
                  ),
                  Container(
                    width: 624,
                    height: 354,
                    padding: EdgeInsets.symmetric(vertical: 10, horizontal: 2),
                    child: MiddleContent(),
                  ),
                  Container(
                    width: 328,
                    height: 354,
                    padding: EdgeInsets.symmetric(vertical: 10, horizontal: 20),
                    decoration: const BoxDecoration(
                      border: Border(
                        left: BorderSide(width: 5, color: Color(0xFF4C6CBF)),
                      ),
                    ),
                    child: RightSwitchContent(),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class BackgroundImage extends StatelessWidget {
  const BackgroundImage({super.key});

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      'assets/images/Cloud background.png',
      fit: BoxFit.contain,
      width: 1280,
      height: 354,
      // Capture the width only once to help calculate looping
      // (assumes full screen width for background tile)
      key: UniqueKey(), // prevents Flutter from recycling
    );
  }
}

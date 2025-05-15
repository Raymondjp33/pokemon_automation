import 'package:flutter/material.dart';

import '../../../constants/app_styles.dart';

class LineItem extends StatelessWidget {
  const LineItem({
    required this.leftText,
    required this.rightText,
    super.key,
  });

  final String leftText;
  final String rightText;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          leftText,
          style: AppTextStyles.pokePixel(fontSize: 30),
        ),
        Spacer(),
        Text(
          rightText,
          style: AppTextStyles.pokePixel(fontSize: 30),
        ),
      ],
    );
  }
}

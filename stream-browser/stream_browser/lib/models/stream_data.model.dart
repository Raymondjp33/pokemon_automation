import 'package:json_annotation/json_annotation.dart';

import 'target.model.dart';

part 'stream_data.model.g.dart';

@JsonSerializable(explicitToJson: true)
class StreamData {
  bool away;

  @JsonKey(name: 'switch1_targets')
  List<TargetModel> switch1Targets;
  @JsonKey(name: 'switch2_targets')
  List<TargetModel> switch2Targets;

  StreamData({
    required this.away,
    this.switch1Targets = const [],
    this.switch2Targets = const [],
  });

  factory StreamData.fromJson(Map<String, dynamic>? json) {
    if (json == null) throw Exception('StreamData: json was null');
    try {
      return _$StreamDataFromJson(json);
    } catch (e, stack) {
      throw 'StreamData.fromJson: $e, $stack';
    }
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> json = _$StreamDataToJson(this);
    return json;
  }
}

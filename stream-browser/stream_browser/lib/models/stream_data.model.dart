import 'package:json_annotation/json_annotation.dart';

part 'stream_data.model.g.dart';

@JsonSerializable(explicitToJson: true)
class StreamData {
  @JsonKey(name: 'switch1_currently_hunting')
  String switch1CurrentlyHunting;
  @JsonKey(name: 'switch2_currently_hunting')
  String switch2CurrentlyHunting;
  bool away;
  @JsonKey(name: 'stream_starttime')
  num streamStarttime;

  @JsonKey(name: 'switch1_gif_number')
  String switch1GifNumber;
  @JsonKey(name: 'switch2_gif_number')
  String switch2GifNumber;

  StreamData({
    required this.switch1CurrentlyHunting,
    required this.switch2CurrentlyHunting,
    required this.away,
    required this.streamStarttime,
    required this.switch1GifNumber,
    required this.switch2GifNumber,
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
